/**
 * Authentication Module Entry Point
 * Main entry point for Authentication functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import Auth modules
import AuthCore from './auth-management/core.js';
import AuthLogin from './auth-management/login.js';
import AuthProfile from './auth-management/profile.js';
import AuthPermissions from './auth-management/permissions.js';

// Global instances
let authCore = null;
let authLogin = null;
let authProfile = null;
let authPermissions = null;

/**
 * Initialize Auth Module
 * Sets up all Authentication components and functionality
 */
export async function initAuthModule() {
    console.log('🚀 Authentication Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Authentication
        authCore = new AuthCore();
        await authCore.init();
        
        // Initialize Login Management
        authLogin = new AuthLogin();
        await authLogin.init();
        
        // Initialize Profile Management
        authProfile = new AuthProfile();
        await authProfile.init();
        
        // Initialize Permissions Management
        authPermissions = new AuthPermissions();
        await authPermissions.init();
        
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
 * Cleanup Auth Module
 */
export function cleanupAuthModule() {
    if (authCore) {
        authCore.destroy();
        authCore = null;
    }
    
    if (authLogin) {
        authLogin.destroy();
        authLogin = null;
    }
    
    if (authProfile) {
        authProfile.destroy();
        authProfile = null;
    }
    
    if (authPermissions) {
        authPermissions.destroy();
        authPermissions = null;
    }
    
    console.log('🧹 Authentication module cleaned up');
}

/**
 * Check if Auth Module is Ready
 */
export function isAuthModuleReady() {
    return authCore && authLogin && authProfile && authPermissions &&
           authCore.isInitialized && authLogin.isInitialized && 
           authProfile.isInitialized && authPermissions.isInitialized;
}

/**
 * Refresh Auth Data
 */
export async function refreshAuthData() {
    if (authCore) {
        await authCore.refreshData();
    }
    
    if (authLogin) {
        await authLogin.refreshLoginStatus();
    }
    
    if (authProfile) {
        await authProfile.refreshProfile();
    }
    
    if (authPermissions) {
        await authPermissions.refreshPermissions();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on an Auth page
    if (window.location.pathname.includes('/auth') || 
        window.location.pathname.includes('/login') ||
        window.location.pathname.includes('/profile') ||
        window.location.pathname.includes('/register')) {
        initAuthModule().catch(error => {
            console.error('Failed to initialize Authentication module:', error);
        });
    }
});

// Export for global access
window.AuthModule = {
    init: initAuthModule,
    cleanup: cleanupAuthModule,
    isReady: isAuthModuleReady,
    refresh: refreshAuthData,
    getCore: getAuthCore,
    getLogin: getAuthLogin,
    getProfile: getAuthProfile,
    getPermissions: getAuthPermissions
};

// Export default
export default {
    init: initAuthModule,
    cleanup: cleanupAuthModule,
    isReady: isAuthModuleReady,
    refresh: refreshAuthData,
    getCore: getAuthCore,
    getLogin: getAuthLogin,
    getProfile: getAuthProfile,
    getPermissions: getAuthPermissions
}; 