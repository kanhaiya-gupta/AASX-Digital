/**
 * Shared Authentication Helper
 * Provides consistent authentication methods for all modules
 */

/**
 * Get the current authentication token from the centralized system
 * @returns {string|null} The authentication token or null if not authenticated
 */
export function getAuthToken() {
    try {
        // Try to get from CoreModule first
        if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
            return window.CoreModule.components.authUI.getAuthState().authToken;
        }
        
        // Fallback to direct storage access
        return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    } catch (error) {
        console.warn('⚠️ Error getting auth token:', error);
        return null;
    }
}

/**
 * Get authentication headers for API requests
 * @returns {Object} Headers object with Authorization header if authenticated
 */
export function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

/**
 * Check if user is currently authenticated
 * @returns {boolean} True if authenticated, false otherwise
 */
export function isAuthenticated() {
    try {
        // Try to get from CoreModule first
        if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
            return window.CoreModule.components.authUI.getAuthState().isAuthenticated;
        }
        
        // Fallback to token check
        const token = getAuthToken();
        return !!token;
    } catch (error) {
        console.warn('⚠️ Error checking authentication:', error);
        return false;
    }
}

/**
 * Get current user information
 * @returns {Object|null} User object or null if not authenticated
 */
export function getCurrentUser() {
    try {
        // Try to get from CoreModule first
        if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
            return window.CoreModule.components.authUI.getAuthState().currentUser;
        }
        
        // Fallback to storage
        const userStr = localStorage.getItem('currentUser');
        return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
        console.warn('⚠️ Error getting current user:', error);
        return null;
    }
}

/**
 * Initialize authentication for a module
 * @param {Object} moduleInstance - The module instance to initialize
 * @param {string} tokenProperty - Property name to store the token (default: 'authToken')
 */
export function initModuleAuth(moduleInstance, tokenProperty = 'authToken') {
    try {
        // Set initial token
        moduleInstance[tokenProperty] = getAuthToken();
        
        // Setup token refresh on auth state changes
        if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
            window.CoreModule.components.authUI.onAuthStateChange(() => {
                moduleInstance[tokenProperty] = getAuthToken();
            });
        }
        
        console.log(`✅ Authentication initialized for ${moduleInstance.constructor.name}`);
    } catch (error) {
        console.warn(`⚠️ Error initializing authentication for ${moduleInstance.constructor.name}:`, error);
    }
}

