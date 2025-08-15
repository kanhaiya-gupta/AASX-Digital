/**
 * Authentication Module - Clean Entry Point
 * @description Simple, predictable initialization for the new modular auth system
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/index
 */

console.log('🚀 New Auth Module Loading - Clean Architecture');

// Import all modules
import AuthManager from './auth-state/auth-manager.js';
import SessionManager from './auth-state/session-manager.js';
import AuthAPI from './auth-services/auth-api.js';
import Validation from './auth-services/validation.js';
import Permissions from './auth-services/permissions.js';
import AuthUIManager from './auth-ui/auth-ui-manager.js';
import AuthComponents from './auth-ui/auth-components.js';
import LoginForm from './auth-forms/login-form.js';
import SignupForm from './auth-forms/signup-form.js';
import ProfileForm from './auth-forms/profile-form.js';
// 🚫 REMOVED: Old auth system import - it was causing conflicts
import PostLoginOrchestrator from './auth-management/post-login-orchestrator.js';

/**
 * Authentication System Manager
 * @description Manages the complete authentication system lifecycle
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
class AuthSystemManager {
    // Private fields
    #isInitialized = false;
    #authManager = null;
    #sessionManager = null;
    #authAPI = null;
    #validation = null;
    #permissions = null;
    #authUI = null;
    #authComponents = null;
    #loginForm = null;
    #signupForm = null;
    #profileForm = null;
    // 🚫 REMOVED: Old auth system property - it was causing conflicts
    #postLoginOrchestrator = null;
    #orchestratorTriggered = false;
    #config = {};
    
    /**
     * Create an AuthSystemManager instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoLogin - Enable auto-demo login
     * @param {string} options.storageKey - Local storage key for tokens
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            autoLogin: options.autoLogin ?? true,
            storageKey: options.storageKey ?? 'auth_token',
            debug: options.debug ?? false
        };
        
        console.log('🔐 AuthSystemManager created with config:', this.#config);
    }
    
    /**
     * Initialize the complete authentication system
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ Auth system already initialized');
                return true;
            }
            
            console.log('🔐 Initializing new clean auth system...');
            
            // Phase 1: Initialize foundation
            console.log('📋 Phase 1: Foundation');
            await this.#initializeFoundation();
            
            // Phase 2: Initialize services
            console.log('📋 Phase 2: Services');
            await this.#initializeServices();
            
            // Phase 3: Initialize UI management
            console.log('📋 Phase 3: UI Management');
            await this.#initializeUI();
            
            // Phase 4: Initialize forms (only on auth page)
            console.log('📋 Phase 4: Form Logic');
            await this.#initializeForms();
            
            // Phase 5: Setup global state
            console.log('📋 Phase 5: Global Setup');
            await this.#setupGlobalState();
            
            this.#isInitialized = true;
            console.log('✅ New auth system initialized successfully!');
            
            // Dispatch ready event
            this.#dispatchReadyEvent();
            
            // CRITICAL FIX: Dispatch global auth system ready event
            // This allows other modules (like Data Manager) to know when auth is ready
            window.dispatchEvent(new CustomEvent('authSystemReady', {
                detail: {
                    authManager: this.#authManager,
                    authAPI: this.#authAPI,
                    authUI: this.#authUI
                }
            }));
            console.log('🚀 Auth system ready event dispatched');
            
            // CRITICAL FIX: Set a flag that other modules can check
            window.authSystemReady = true;
            console.log('🚀 Auth system ready flag set');
            
            // CRITICAL FIX: Immediately check for stored tokens and restore session
            // This ensures that if a user was previously logged in, their session is restored
            if (this.#authManager) {
                console.log('🔐 Auth system: Checking for stored tokens...');
                try {
                    // Trigger a session check to restore any stored authentication
                    // Note: We can't call initialize() again, so we'll trigger the session check manually
                    const token = this.#authManager.getStoredToken();
                    console.log('🔍 Auth system: Token check result:', token ? `Found token: ${token.substring(0, 20)}...` : 'No token found');
                    
                    if (token) {
                        console.log('🔑 Auth system: Found stored token, triggering session restoration...');
                        // CRITICAL FIX: Actually restore the session using the public method
                        console.log('🔍 Auth system: Calling restoreSessionFromToken...');
                        const restored = await this.#authManager.restoreSessionFromToken(token);
                        console.log('🔍 Auth system: restoreSessionFromToken result:', restored);
                        
                        if (restored) {
                            console.log('✅ Auth system: Session restored successfully');
                        } else {
                            console.log('⚠️ Auth system: Session restoration failed');
                        }
                    } else {
                        console.log('🔐 Auth system: No stored token found');
                    }
                    console.log('✅ Auth system: Session check completed');
                } catch (error) {
                    console.warn('⚠️ Auth system: Session check failed:', error);
                }
            }
            
            return true;
            
        } catch (error) {
            console.error('❌ Auth system initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Initialize foundation modules
     * @private
     */
    async #initializeFoundation() {
        this.#authManager = new AuthManager();
        this.#sessionManager = new SessionManager();
        // 🚫 REMOVED: Old auth system initialization - it was causing conflicts
        this.#postLoginOrchestrator = new PostLoginOrchestrator();
        
        // Initialize foundation modules
        await this.#authManager.initialize();
        await this.#sessionManager.initialize();
        // 🚫 REMOVED: Old auth system init call - it was causing conflicts
        // PostLoginOrchestrator auto-initializes, no need to call initialize()
    }
    
    /**
     * Initialize service modules
     * @private
     */
    async #initializeServices() {
        this.#authAPI = new AuthAPI();
        this.#validation = new Validation();
        this.#permissions = new Permissions();
        
        // Initialize service modules
        await this.#authAPI.initialize();
        await this.#validation.initialize();
        await this.#permissions.initialize();
    }
    
    /**
     * Initialize UI management modules
     * @private
     */
    async #initializeUI() {
        this.#authUI = new AuthUIManager();
        this.#authComponents = new AuthComponents();
        
        // Initialize UI modules
        await this.#authUI.initialize();
        await this.#authComponents.initialize();
    }
    
    /**
     * Initialize form modules (only on auth page)
     * @private
     */
    async #initializeForms() {
        // Check if we're on the auth page (multiple possible paths)
        const isAuthPage = window.location.pathname === '/auth' || 
                          window.location.pathname === '/api/auth' ||
                          window.location.pathname.includes('auth');
        
        if (isAuthPage) {
            console.log('🔐 On auth page - initializing forms');
            
            try {
                this.#loginForm = new LoginForm();
                this.#signupForm = new SignupForm();
                this.#profileForm = new ProfileForm();
                
                // Initialize forms
                await this.#loginForm.initialize();
                await this.#signupForm.initialize();
                await this.#profileForm.initialize();
                
                console.log('✅ All forms initialized successfully');
                
            } catch (error) {
                console.error('❌ Form initialization failed:', error);
                // Don't fail the entire system if forms fail
            }
            
        } else {
            console.log('🌐 On other page - skipping forms');
        }
    }
    
    /**
     * Setup global state and expose modules
     * @private
     */
    async #setupGlobalState() {
        // Expose globally for other modules
        window.authManager = this.#authManager;
        window.authAPI = this.#authAPI;
        window.authUI = this.#authUI;
        window.authValidation = this.#validation;
        window.authPermissions = this.#permissions;
        // 🚫 REMOVED: Old auth system global exposure - it was causing conflicts
        window.postLoginOrchestrator = this.#postLoginOrchestrator;
        
        // Setup global event listeners
        this.#setupGlobalEventListeners();
        
        // CRITICAL FIX: Synchronize authentication state after setup
        await this.#synchronizeAuthState();
    }
    
    /**
     * Synchronize authentication state after system initialization
     * @private
     */
    async #synchronizeAuthState() {
        try {
            console.log('🔄 Synchronizing authentication state...');
            
            // Wait a bit for all modules to be ready
            await new Promise(resolve => setTimeout(resolve, 100));
            
            if (this.#authManager && this.#authUI) {
                const sessionInfo = this.#authManager.getSessionInfo();
                console.log('📋 Current session info:', sessionInfo);
                
                // Update UI to reflect current authentication state
                this.#authUI.updateUI(sessionInfo);
                
                console.log('✅ Authentication state synchronized');
            } else {
                console.log('⚠️ Auth manager or UI not ready for synchronization');
            }
            
        } catch (error) {
            console.error('❌ Authentication state synchronization failed:', error);
        }
    }
    
    /**
     * Setup global event listeners
     * @private
     */
    #setupGlobalEventListeners() {
        // Listen for auth state changes
        window.addEventListener('authStateChanged', (event) => {
            console.log('🔄 Auth state changed:', event.detail);
            this.#handleAuthStateChange(event.detail);
        });
        
        // Listen for logout requests
        window.addEventListener('logoutRequested', (event) => {
            console.log('🚪 Logout requested');
            this.#handleLogout();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async (event) => {
            console.log('✅ Login success:', event.detail);
            try {
                await this.#handleLoginSuccess(event.detail);
            } catch (error) {
                console.error('❌ Auth System: Failed to handle login success:', error);
            }
        });
        
        // Listen for signup success
        window.addEventListener('signupSuccess', (event) => {
            console.log('✅ Signup success:', event.detail);
            this.#handleSignupSuccess(event.detail);
        });
        
        // Listen for profile updates
        window.addEventListener('profileUpdated', (event) => {
            console.log('✅ Profile updated:', event.detail);
            this.#handleProfileUpdated(event.detail);
        });
        
        // Listen for password changes
        window.addEventListener('passwordChanged', (event) => {
            console.log('✅ Password changed:', event.detail);
            this.#handlePasswordChanged(event.detail);
        });
    }
    
    /**
     * Handle authentication state changes
     * @param {Object} state - New auth state
     * @private
     */
    async #handleAuthStateChange(state) {
        if (this.#authUI) {
            this.#authUI.updateUI(state);
        }
        
        // 🎭 TRIGGER PostLoginOrchestrator when session is restored
        if (state.isAuthenticated && this.#postLoginOrchestrator && !this.#orchestratorTriggered) {
            console.log('🎭 Auth System: Session restored, triggering PostLoginOrchestrator...');
            console.log('🔧 Auth System: Auth state:', state);
            
            try {
                // Mark as triggered to prevent duplicate calls
                this.#orchestratorTriggered = true;
                
                // Trigger orchestrator for session restoration
                await this.#postLoginOrchestrator.handleLoginSuccess({
                    user: state.user,
                    sessionRestored: true,
                    timestamp: Date.now()
                });
                
                console.log('✅ Auth System: PostLoginOrchestrator completed for session restoration');
                
            } catch (orchestratorError) {
                console.error('❌ Auth System: PostLoginOrchestrator failed for session restoration:', orchestratorError);
                // Reset flag to allow retry
                this.#orchestratorTriggered = false;
                
                // 🚫 NO REDIRECT ON FAILURE!
                console.error('🚫 Auth System: Session restoration orchestration failed - NOT redirecting!');
                console.error('🚫 Auth System: User must stay on current page until orchestration is fixed');
            }
        }
    }
    
    /**
     * Handle logout requests
     * @private
     */
    async #handleLogout() {
        try {
            if (this.#sessionManager) {
                await this.#sessionManager.logout();
            }
            
            if (this.#authUI) {
                this.#authUI.showUnauthenticatedState();
            }
            
            console.log('✅ Logout completed');
            
        } catch (error) {
            console.error('❌ Logout failed:', error);
        }
    }
    
    /**
     * Handle login success
     * @private
     */
    async #handleLoginSuccess(detail) {
        try {
            console.log('🎉 Auth System: Login success detected, starting post-login orchestration...');
            console.log('📋 Login details:', detail);
            
            // 1. Update AuthManager with user authentication
            if (this.#authManager) {
                console.log('🔐 Auth System: Updating AuthManager with user authentication...');
                try {
                    this.#authManager.authenticateUser(detail.token, detail.user);
                    console.log('✅ Auth System: AuthManager updated successfully');
                } catch (error) {
                    console.error('❌ Auth System: Failed to update AuthManager:', error);
                }
            } else {
                console.warn('⚠️ Auth System: AuthManager not available for authentication update');
            }
            
            // 2. Update UI to authenticated state
            if (this.#authUI) {
                console.log('🎨 Auth System: Updating UI to authenticated state...');
                this.#authUI.showAuthenticatedState();
                console.log('✅ Auth System: UI updated successfully');
            } else {
                console.warn('⚠️ Auth System: AuthUI not available for state update');
            }
            
            // 2. TRIGGER PostLoginOrchestrator and WAIT for completion
            if (this.#postLoginOrchestrator) {
                console.log('🎭 Auth System: PostLoginOrchestrator available, triggering orchestration...');
                console.log('🔧 Auth System: Orchestrator status:', this.#postLoginOrchestrator.getStatus());
                
                try {
                    // Wait for orchestrator to complete
                    console.log('⏳ Auth System: Waiting for PostLoginOrchestrator to complete...');
                    await this.#postLoginOrchestrator.handleLoginSuccess(detail);
                    
                    console.log('✅ Auth System: PostLoginOrchestrator SUCCESS! All user data loaded.');
                    console.log('📊 Auth System: Final orchestrator status:', this.#postLoginOrchestrator.getStatus());
                    
                    // 3. SUCCESS → Redirect to homepage with data ready
                    console.log('🚀 Auth System: Orchestration completed successfully, redirecting to homepage...');
                    window.location.href = '/api/dashboard';
                    
                } catch (orchestratorError) {
                    console.error('❌ Auth System: PostLoginOrchestrator FAILED:', orchestratorError);
                    console.error('🔍 Auth System: Orchestrator error details:', {
                        message: orchestratorError.message,
                        stack: orchestratorError.stack,
                        orchestratorStatus: this.#postLoginOrchestrator.getStatus()
                    });
                    
                    // Don't redirect if orchestration fails
                    console.warn('⚠️ Auth System: Not redirecting due to orchestration failure');
                    // You can add error handling here - show error message, retry button, etc.
                }
                
            } else {
                console.error('❌ Auth System: PostLoginOrchestrator not available!');
                console.error('🔍 Auth System: Debug info:', {
                    postLoginOrchestrator: this.#postLoginOrchestrator,
                    // 🚫 REMOVED: Old auth system reference - it was causing conflicts
                    authManager: this.#authManager,
                    sessionManager: this.#sessionManager
                });
                
                // 🚫 NO REDIRECT ON FAILURE!
                console.error('🚫 Auth System: PostLoginOrchestrator not available - NOT redirecting!');
                console.error('🚫 Auth System: User must stay on current page until orchestration is fixed');
                
                // You can add error handling here:
                // - Show error message to user
                // - Add retry button
                // - Log the issue for debugging
                // - But NEVER redirect without data loading
            }
            
            console.log('✅ Auth System: Login success handling completed successfully');
            
        } catch (error) {
            console.error('❌ Auth System: Login success handling failed:', error);
            console.error('🔍 Auth System: Error details:', {
                message: error.message,
                stack: error.stack,
                detail: detail,
                postLoginOrchestrator: this.#postLoginOrchestrator,
                // 🚫 REMOVED: Old auth system reference - it was causing conflicts
            });
            
            // Don't redirect if there's an error
            console.warn('⚠️ Auth System: Not redirecting due to error in login success handling');
        }
    }
    
    /**
     * Handle signup success
     * @private
     */
    #handleSignupSuccess(detail) {
        try {
            console.log('🎉 New user registered:', detail.username);
            // Forms will handle their own success messages
        } catch (error) {
            console.error('❌ Signup success handling failed:', error);
        }
    }
    
    /**
     * Handle profile updates
     * @private
     */
    #handleProfileUpdated(detail) {
        try {
            if (this.#authUI) {
                this.#authUI.updateUserInfo(detail.user);
            }
            console.log('✅ Profile updated successfully');
        } catch (error) {
            console.error('❌ Profile update handling failed:', error);
        }
    }
    
    /**
     * Handle password changes
     * @private
     */
    #handlePasswordChanged(detail) {
        try {
            console.log('✅ Password changed successfully');
            // Could trigger additional security measures here
        } catch (error) {
            console.error('❌ Password change handling failed:', error);
        }
    }
    
    /**
     * Dispatch ready event
     * @private
     */
    #dispatchReadyEvent() {
        window.dispatchEvent(new CustomEvent('authSystemReady', {
            detail: {
                authManager: this.#authManager,
                authAPI: this.#authAPI,
                authUI: this.#authUI,
                validation: this.#validation,
                permissions: this.#permissions
            }
        }));
    }
    
    /**
     * Check if the system is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get the auth manager instance
     * @readonly
     * @returns {AuthManager} Auth manager instance
     */
    get authManager() {
        return this.#authManager;
    }
    
    /**
     * Get the auth API instance
     * @readonly
     * @returns {AuthAPI} Auth API instance
     */
    get authAPI() {
        return this.#authAPI;
    }
    
    /**
     * Get the auth UI manager instance
     * @readonly
     * @returns {AuthUIManager} Auth UI manager instance
     */
    get authUI() {
        return this.#authUI;
    }
    
    /**
     * Get the login form instance
     * @readonly
     * @returns {LoginForm|null} Login form instance
     */
    get loginForm() {
        return this.#loginForm;
    }
    
    /**
     * Get the signup form instance
     * @readonly
     * @returns {SignupForm|null} Signup form instance
     */
    get signupForm() {
        return this.#signupForm;
    }
    
    /**
     * Get the profile form instance
     * @readonly
     * @returns {ProfileForm|null} Profile form instance
     */
    get profileForm() {
        return this.#profileForm;
    }

    /**
     * Check if the auth system is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get system status for debugging
     * @returns {Object} System status information
     */
    getSystemStatus() {
        return {
            isInitialized: this.#isInitialized,
            config: this.#config,
            modules: {
                authManager: !!this.#authManager,
                sessionManager: !!this.#sessionManager,
                authAPI: !!this.#authAPI,
                validation: !!this.#validation,
                permissions: !!this.#permissions,
                authUI: !!this.#authUI,
                authComponents: !!this.#authComponents
            },
            forms: {
                loginForm: !!this.#loginForm,
                signupForm: !!this.#signupForm,
                profileForm: !!this.#profileForm
            }
        };
    }
    
    /**
     * Create a default auth system instance
     * @static
     * @returns {AuthSystemManager} New instance with default config
     */
    static createDefault() {
        return new AuthSystemManager({
            autoLogin: true,
            storageKey: 'auth_token',
            debug: false
        });
    }
}

// Create and initialize the auth system
const authSystem = AuthSystemManager.createDefault();

/**
 * Initialize the authentication system
 * @description Main initialization function - called when DOM is ready
 */
async function initializeAuth() {
    try {
        await authSystem.initialize();
        console.log('🎉 Auth system ready!');
    } catch (error) {
        console.error('❌ Auth system initialization failed:', error);
        // Don't crash the page - auth is optional
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAuth);
} else {
    initializeAuth();
}

// Export for testing and external use
export { initializeAuth, authSystem, AuthSystemManager };
