/**
 * Authentication Module - Main Entry Point
 * Handles all authentication functionality including login, signup, profile management, and admin controls
 */

// Import UI Components
import LoginForm from './ui-components/login-form.js';
import SignupForm from './ui-components/signup-form.js';

// Import Auth Management
import AuthCore from './auth-management/core.js';
import AuthLogin from './auth-management/login.js';
import AuthProfile from './auth-management/profile.js';
import AuthPermissions from './auth-management/permissions.js';

// Global instances
let authCore = null;
let authLogin = null;
let authProfile = null;
let authPermissions = null;
let loginForm = null;
let signupForm = null;

/**
 * Initialize Authentication Module
 */
export async function initAuthModule() {
    console.log('🚀 Authentication Module initializing...');
    
    try {
        // Initialize Core Authentication
        authCore = new AuthCore();
        await authCore.init();
        
        // Initialize Login Management with authCore instance
        authLogin = new AuthLogin(authCore);
        await authLogin.init();
        
        // Initialize Profile Management with authCore instance
        authProfile = new AuthProfile(authCore);
        await authProfile.init();
        
        // Initialize Permissions Management with authCore instance
        authPermissions = new AuthPermissions(authCore);
        await authPermissions.init();
        
        // Initialize UI Components
        loginForm = new LoginForm();
        loginForm.init();
        
        signupForm = new SignupForm();
        signupForm.init();
        
        // Setup global event listeners
        setupGlobalEventListeners();
        
        console.log('✅ Authentication Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('authModuleReady', {
            detail: {
                authCore,
                authLogin,
                authProfile,
                authPermissions
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
                authProfile.loadUserProfile();
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
        
        // Redirect to login page
        window.location.href = '/auth';
        
    } catch (error) {
        console.error('❌ Logout failed:', error);
        // Force redirect anyway
        window.location.href = '/auth';
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
        window.location.href = '/auth';
        return false;
    }
    return true;
}

/**
 * Require Admin Role
 */
export function requireAdmin() {
    if (!checkAuthStatus()) {
        window.location.href = '/auth';
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
window.checkAuthStatus = checkAuthStatus;
window.getCurrentUser = getCurrentUser;
window.requireAuth = requireAuth;
window.requireAdmin = requireAdmin;

// Initialize module when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the auth page
    if (window.location.pathname.includes('/auth')) {
        initAuthModule().catch(error => {
            console.error('Failed to initialize auth module:', error);
        });
    }
});

// Export for use in other modules
export default {
    initAuthModule,
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