/**
 * Authentication Module - Main Entry Point
 * Handles all authentication functionality including login, signup, profile management, and admin controls
 * CACHE BUST: 2025-08-10-21:22
 */

// Test if this script is loading at all
console.log('🔍 Auth module file loaded at:', new Date().toISOString());
console.log('🔍 Current pathname:', window.location.pathname);
console.log('🔍 Script execution started');

// Simple test to ensure script is running
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 DOM Content Loaded event fired');
});

// Global instances - declare these first
let authCore = null;
let authLogin = null;
let authProfile = null;
let authPermissions = null;
let loginForm = null;
let signupForm = null;

// Initialize the module
(async function initAuthModuleImports() {
    // Import UI Components with error handling
    let LoginForm, SignupForm, AuthCore, AuthLogin, AuthProfile, AuthPermissions;
    const cacheBust = new Date().getTime();  // Unique timestamp per page load

    try {
        console.log('🔍 Attempting to import UI Components...');
        const loginFormModule = await import(`./ui-components/login-form.js?cache=${cacheBust}`);
        LoginForm = loginFormModule.LoginForm; // Named export
        console.log('✅ LoginForm imported successfully');
        
        SignupForm = (await import(`./ui-components/signup-form.js?cache=${cacheBust}`)).default; // Default export
        console.log('✅ SignupForm imported successfully');
        
        console.log('🔍 Attempting to import Auth Management...');
        AuthCore = (await import(`./auth-management/core.js?cache=${cacheBust}`)).default;
        console.log('✅ AuthCore imported successfully');
        
        AuthLogin = (await import(`./auth-management/login.js?cache=${cacheBust}`)).default;
        console.log('✅ AuthLogin imported successfully');
        
        AuthProfile = (await import(`./auth-management/profile.js?cache=${cacheBust}`)).default;
        console.log('✅ AuthProfile imported successfully');
        
        AuthPermissions = (await import(`./auth-management/permissions.js?cache=${cacheBust}`)).default;
        console.log('✅ AuthPermissions imported successfully');
        
        console.log('✅ All imports successful, proceeding with initialization...');
        
        // Debug what we actually imported
        console.log('🔍 Imported classes:', {
            LoginForm: typeof LoginForm,
            SignupForm: typeof SignupForm,
            LoginFormValue: LoginForm,
            SignupFormValue: SignupForm
        });
        
        // Assign the imported classes to global variables
        authCore = AuthCore;
        authLogin = AuthLogin;
        authProfile = AuthProfile;
        authPermissions = AuthPermissions;
        loginForm = LoginForm;
        signupForm = SignupForm;
        
        // Also assign to window for debugging
        window.authCore = AuthCore;
        window.authLogin = AuthLogin;
        window.authProfile = AuthProfile;
        window.authPermissions = AuthPermissions;
        window.loginForm = LoginForm;
        window.signupForm = SignupForm;
        
        console.log('✅ Global variables assigned:', {
            authCore: !!authCore,
            authLogin: !!authLogin,
            authProfile: !!authProfile,
            authPermissions: !!authPermissions,
            loginForm: !!loginForm,
            signupForm: !!signupForm
        });
        
        console.log('🔍 Global variable details:', {
            loginForm: typeof loginForm,
            signupForm: typeof signupForm,
            loginFormValue: loginForm,
            signupFormValue: signupForm
        });
        
        console.log('🔍 Detailed authCore info:', {
            type: typeof authCore,
            isFunction: typeof authCore === 'function',
            isConstructor: authCore && typeof authCore === 'function' && authCore.prototype && authCore.prototype.constructor,
            prototype: authCore ? authCore.prototype : null,
            constructor: authCore ? authCore.prototype?.constructor : null
        });
        
        console.log('✅ Global variables assigned, proceeding with initialization...');
        
        // Now proceed with the rest of the module
        try {
            await setupAuthModule();
            console.log('✅ setupAuthModule completed successfully');
            
            // Call the path check function after initialization
            checkPathAndInit();
        } catch (error) {
            console.error('❌ setupAuthModule failed:', error);
            // Don't rethrow - let the error be handled gracefully
        }
        
    } catch (error) {
        console.error('❌ Import failed:', error);
        console.error('❌ Import error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        return; // Exit if imports fail
        }
})();

// Function to check path and initialize if on auth page
function checkPathAndInit() {
    const normalizedPath = window.location.pathname.replace(/\/$/, ''); // Remove trailing slash
    console.log('🔍 Checking path:', window.location.pathname, 'Normalized:', normalizedPath);

    if (normalizedPath === '/api/auth') {
        console.log('🔐 Auth page detected, checking if auth module is ready...');
        
        // Check if auth module is already initialized
        if (authCore && authLogin && authProfile && authPermissions) {
            console.log('🔍 Auth module already initialized, proceeding...');
            // Module is already initialized, no need to call setupAuthModule again
        } else {
            console.log('🔍 Auth module not ready yet, waiting...');
            // Wait for the module to be ready
            const checkReady = setInterval(() => {
                if (authCore && authLogin && authProfile && authPermissions) {
                    console.log('🔍 Auth module now ready');
                    clearInterval(checkReady);
                }
            }, 100);
        }
    } else {
        console.log('🔍 Not on auth page, skipping initialization');
    }
}

/**
 * Initialize Authentication Module
 */
async function setupAuthModule() {
    console.log('🚀 Authentication Module initializing...');
    
    try {
        // Check if global variables are properly assigned
        if (!authCore || !authLogin || !authProfile || !authPermissions) {
            console.error('❌ Global variables not properly initialized:', {
                authCore: !!authCore,
                authLogin: !!authLogin,
                authProfile: !!authProfile,
                authPermissions: !!authPermissions
            });
            throw new Error('Global variables not initialized');
        }
        
        console.log('🔍 Global variables check passed, proceeding with initialization...');
        console.log('🔍 authCore type:', typeof authCore, 'Constructor:', authCore.prototype?.constructor?.name);
        
        // Initialize Core Authentication
        const authCoreInstance = new authCore();
        await authCoreInstance.init();
        
        // Set global authCore for other modules to access
        window.authCore = authCoreInstance;
        
        // Set AuthUIManager in the core module
        if (window.setAuthUIManager && authCoreInstance.getAuthUIManager) {
            try {
                const authUI = await authCoreInstance.getAuthUIManager();
                if (authUI) {
                    window.setAuthUIManager(authUI);
                    console.log('✅ AuthUIManager set in core module');
                } else {
                    console.warn('⚠️ AuthUIManager not available');
                }
            } catch (error) {
                console.error('❌ Failed to get AuthUIManager:', error);
            }
        }
        
        // Initialize Login Management with authCore instance
        const authLoginInstance = new authLogin(authCoreInstance);
        await authLoginInstance.init();
        
        // Initialize Profile Management with authCore instance (only if user is authenticated)
        const authProfileInstance = new authProfile(authCoreInstance);
        // Don't initialize profile management for unauthenticated users
        if (authCoreInstance.isUserAuthenticated()) {
            await authProfileInstance.init();
        } else {
            console.log('👤 Skipping profile management initialization - user not authenticated');
        }
        
        // Initialize Permissions Management with authCore instance
        const authPermissionsInstance = new authPermissions(authCoreInstance);
        await authPermissionsInstance.init();
        
        // Initialize UI Components
        console.log('🔍 Before UI Components initialization:', {
            loginForm: typeof loginForm,
            signupForm: typeof signupForm,
            LoginForm: typeof LoginForm,
            SignupForm: typeof SignupForm
        });
        
        if (typeof loginForm !== 'function') {
            console.error('❌ loginForm is not a constructor:', loginForm);
            throw new Error('loginForm is not a constructor');
        }
        
        if (typeof signupForm !== 'function') {
            console.error('❌ signupForm is not a constructor:', signupForm);
            throw new Error('signupForm is not a constructor');
        }
        
        console.log('🔍 Creating LoginForm instance...');
        const loginFormInstance = new loginForm();
        loginFormInstance.init();
        
        console.log('🔍 Creating SignupForm instance...');
        const signupFormInstance = new signupForm();
        signupFormInstance.init();
        
        // Setup global event listeners
        setupGlobalEventListeners();
        
        // Clear any stored tokens to ensure clean state
        try {
            localStorage.removeItem('auth_token');
            sessionStorage.removeItem('auth_token');
            console.log('🧹 Cleared any stored authentication tokens');
        } catch (error) {
            console.warn('⚠️ Could not clear stored tokens:', error);
        }
        
        // Force the login tab to be active for unauthenticated users
        if (!authCoreInstance.isUserAuthenticated()) {
            console.log('🔐 User not authenticated, forcing login tab to be active');
            // Use setTimeout to ensure DOM is ready
            setTimeout(() => {
                const loginTab = new bootstrap.Tab(document.getElementById('login-tab'));
                loginTab.show();
            }, 100);
        } else {
            console.log('🔐 User is authenticated, but forcing login tab to be active for now');
            // Even if authenticated, show login tab to prevent confusion
            setTimeout(() => {
                const loginTab = new bootstrap.Tab(document.getElementById('login-tab'));
                loginTab.show();
            }, 100);
        }
        
        console.log('✅ Authentication Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('authModuleReady', {
            detail: {
                authCore: authCoreInstance,
                authLogin: authLoginInstance,
                authProfile: authProfileInstance,
                authPermissions: authPermissionsInstance
            }
        }));
        
    } catch (error) {
        console.error('❌ Authentication module initialization failed:', error);
        throw error;
    }
}

/**
 * Setup global event listeners
 */
function setupGlobalEventListeners() {
    // Tab navigation
    const authTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    authTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', (e) => {
            const target = e.target.getAttribute('data-bs-target');
            handleTabChange(target);
        });
    });
    
    // Refresh button
    const refreshBtn = document.querySelector('[onclick="refreshAuthData()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshAuthData);
    }
    
    // Add user button
    const addUserBtn = document.querySelector('[data-bs-target="#createUserModal"]');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', () => {
            // Initialize user creation modal
            console.log('Opening user creation modal');
        });
    }
}

/**
 * Handle tab changes
 */
function handleTabChange(targetId) {
    console.log(`Switched to tab: ${targetId}`);
    
    switch (targetId) {
        case '#login':
            if (loginForm) {
                loginForm.reset();
            }
            break;
        case '#signup':
            if (signupForm) {
                signupForm.reset();
            }
            break;
        case '#profile':
            if (authProfile) {
                authProfile.loadProfileData();
            }
            break;
        case '#admin':
            if (authPermissions) {
                authPermissions.loadAdminData();
            }
            break;
    }
}

/**
 * Get Auth Core Instance
 */
export function getAuthCore() {
    return authCore;
}

/**
 * Get Login Management Instance
 */
export function getAuthLogin() {
    return authLogin;
}

/**
 * Get Profile Management Instance
 */
export function getAuthProfile() {
    return authProfile;
}

/**
 * Get Permissions Management Instance
 */
export function getAuthPermissions() {
    return authPermissions;
}

/**
 * Get Login Form Instance
 */
export function getLoginForm() {
    return loginForm;
}

/**
 * Get Signup Form Instance
 */
export function getSignupForm() {
    return signupForm;
}

/**
 * Check if Auth Module is ready
 */
export function isAuthModuleReady() {
    return authCore !== null && authCore.isInitialized;
}

/**
 * Refresh Auth Data
 */
export async function refreshAuthData() {
    console.log('🔄 Refreshing authentication data...');
    
    try {
        if (authCore) {
            await authCore.refreshData();
        }
        
        if (authProfile) {
            await authProfile.refreshProfile();
        }
        
        if (authPermissions) {
            await authPermissions.refreshPermissions();
        }
        
        console.log('✅ Authentication data refreshed');
        
    } catch (error) {
        console.error('❌ Failed to refresh authentication data:', error);
    }
}

/**
 * Show Login Tab
 */
export function showLoginTab() {
    const loginTab = new bootstrap.Tab(document.getElementById('login-tab'));
    loginTab.show();
}

/**
 * Show Signup Tab
 */
export function showSignupTab() {
    const signupTab = new bootstrap.Tab(document.getElementById('signup-tab'));
    signupTab.show();
}

/**
 * Show Profile Tab
 */
export function showProfileTab() {
    const profileTab = new bootstrap.Tab(document.getElementById('profile-tab'));
    profileTab.show();
}

/**
 * Show Admin Tab
 */
export function showAdminTab() {
    const adminTab = new bootstrap.Tab(document.getElementById('admin-tab'));
    adminTab.show();
}

/**
 * Logout User
 */
export async function logoutUser() {
    try {
        if (authCore) {
            await authCore.logout();
        }
        
        // Redirect to main page instead of auth page to avoid loops
        window.location.href = '/';
        
    } catch (error) {
        console.error('❌ Logout failed:', error);
        // Force redirect anyway
        window.location.href = '/';
    }
}

/**
 * Check Authentication Status
 */
export function checkAuthStatus() {
    if (authCore) {
        return authCore.isUserAuthenticated();
    }
    return false;
}

/**
 * Get Current User
 */
export function getCurrentUser() {
    if (authCore) {
        return authCore.getCurrentUser();
    }
    return null;
}

/**
 * Require Authentication
 */
export function requireAuth() {
    if (!checkAuthStatus()) {
        window.location.href = '/api/auth/';
        return false;
    }
    return true;
}

/**
 * Require Admin Role
 */
export function requireAdmin() {
    if (!checkAuthStatus()) {
        window.location.href = '/api/auth/';
        return false;
    }
    
    const user = getCurrentUser();
    if (!user || user.role !== 'admin') {
        window.location.href = '/';
        return false;
    }
    return true;
}

/**
 * Cleanup Auth Module
 */
export function cleanupAuthModule() {
    console.log('🧹 Cleaning up Authentication Module...');
    
    if (authCore) {
        authCore.destroy();
    }
    
    if (authLogin) {
        authLogin.destroy();
    }
    
    if (authProfile) {
        authProfile.destroy();
    }
    
    if (authPermissions) {
        authPermissions.destroy();
    }
    
    if (loginForm) {
        loginForm.destroy();
    }
    
    if (signupForm) {
        signupForm.destroy();
    }
    
    console.log('✅ Authentication Module cleaned up');
}

// Global functions for HTML onclick handlers
window.showLoginTab = showLoginTab;
window.showSignupTab = showSignupTab;
window.showProfileTab = showProfileTab;
window.showAdminTab = showAdminTab;
window.refreshAuthData = refreshAuthData;
window.logoutUser = logoutUser;
window.logout = logoutUser; // Alias for HTML onclick handlers
window.checkAuthStatus = checkAuthStatus;
window.getCurrentUser = getCurrentUser;
window.requireAuth = requireAuth;
window.requireAdmin = requireAdmin;

// Improved path detection with debug logging
// const normalizedPath = window.location.pathname.replace(/\/$/, ''); // Remove trailing slash
// console.log('🔍 Checking path:', window.location.pathname, 'Normalized:', normalizedPath);

// if (normalizedPath === '/api/auth') {
//     console.log('🔐 Auth page detected, initializing auth module...');
    
//     // Wait for CoreModule to be ready
//     if (window.CoreModule && window.CoreModule.isInitialized) {
//         console.log('🔍 CoreModule already initialized, proceeding...');
//         setupAuthModule();
//     } else {
//         console.log('🔍 Waiting for coreModuleReady event...');
//         window.addEventListener('coreModuleReady', () => {
//             console.log('🔍 Received coreModuleReady event');
//             setupAuthModule();
//         });
//     }
// } else {
//     console.log('🔍 Not on auth page, skipping initialization');
// }

// Removed duplicate initialization logic - now handled by checkPathAndInit() function

// Export for use in other modules
export default {
    initAuthModule: setupAuthModule, // Changed to setupAuthModule
    getAuthCore,
    getAuthLogin,
    getAuthProfile,
    getAuthPermissions,
    getLoginForm,
    getSignupForm,
    isAuthModuleReady,
    refreshAuthData,
    showLoginTab,
    showSignupTab,
    showProfileTab,
    showAdminTab,
    logoutUser,
    checkAuthStatus,
    getCurrentUser,
    requireAuth,
    requireAdmin,
    cleanupAuthModule
}; 