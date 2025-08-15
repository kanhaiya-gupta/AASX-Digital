/**
 * Authentication Manager - Global Authentication State Management
 * @description Manages global authentication state across all pages
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-state/auth-manager
 */

/**
 * Authentication State Manager
 * @description Manages global authentication state and user information
 * @class AuthManager
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class AuthManager {
    // Private fields
    #isInitialized = false;
    #isAuthenticated = false;
    #currentUser = null;
    #userRole = null;
    #userPermissions = [];
    #lastActivity = null;
    #config = {};
    #eventListeners = new Map();
    #sessionMonitor = null;
    #activityMonitor = null;
    
    /**
     * Create an AuthManager instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoLogin - Enable auto-demo login
     * @param {string} options.storageKey - Local storage key for tokens
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            autoLogin: options.autoLogin ?? true,
            storageKey: options.storageKey ?? 'auth_token',
            debug: options.debug ?? false,
            sessionTimeout: options.sessionTimeout ?? 24 * 60 * 60 * 1000, // 24 hours
            activityTimeout: options.activityTimeout ?? 30 * 60 * 1000 // 30 minutes
        };
        
        console.log('🔐 AuthManager created with config:', this.#config);
    }
    
    /**
     * Initialize the authentication manager
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ AuthManager already initialized');
                return true;
            }
            
            console.log('🔐 Initializing AuthManager...');
            
            // Check for existing session
            await this.#checkExistingSession();
            
            // Setup session monitoring
            this.#setupSessionMonitoring();
            
            // Setup activity monitoring
            this.#setupActivityMonitoring();
            
            this.#isInitialized = true;
            console.log('✅ AuthManager initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ AuthManager initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Check for existing authentication session
     * @private
     */
    async #checkExistingSession() {
        try {
            const token = this.#getStoredToken();
            
            if (token) {
                console.log('🔑 Found stored token, validating...');
                console.log('🔑 Token preview:', token.substring(0, 50) + '...');
                
                if (await this.#validateToken(token)) {
                    console.log('✅ Token validation successful, restoring session...');
                    await this.#restoreSession(token);
                    console.log('✅ Session restored successfully');
                } else {
                    console.log('❌ Stored token is invalid, clearing...');
                    this.#clearSession();
                }
            } else {
                console.log('🔐 No stored token found');
                
                if (this.#config.autoLogin) {
                    console.log('🎭 Attempting auto-demo login...');
                    await this.#attemptAutoDemoLogin();
                }
            }
            
        } catch (error) {
            console.error('❌ Session check failed:', error);
            this.#clearSession();
        }
    }
    
    /**
     * Get stored authentication token
     * @private
     * @returns {string|null} Stored token or null
     */
    #getStoredToken() {
        try {
            // Check sessionStorage first (for demo users)
            let token = sessionStorage.getItem(this.#config.storageKey);
            
            if (!token) {
                // Fallback to localStorage
                token = localStorage.getItem(this.#config.storageKey);
            }
            
            return token;
        } catch (error) {
            console.warn('⚠️ Could not retrieve stored token:', error);
            return null;
        }
    }
    
    /**
     * Validate authentication token
     * @private
     * @param {string} token - JWT token to validate
     * @returns {Promise<boolean>} Token validity
     */
    async #validateToken(token) {
        try {
            console.log('🔍 Validating token...');
            
            // Basic JWT structure validation
            if (!token || typeof token !== 'string' || !token.includes('.')) {
                console.log('❌ Token structure invalid');
                return false;
            }
            
            // Check if token is expired
            const payload = this.#decodeJWT(token);
            if (!payload || !payload.exp) {
                console.log('❌ Token payload invalid or missing exp:', payload);
                return false;
            }
            
            console.log('🔍 Token payload:', payload);
            
            const currentTime = Math.floor(Date.now() / 1000);
            if (payload.exp < currentTime) {
                console.log('⏰ Token expired. Exp:', payload.exp, 'Current:', currentTime);
                return false;
            }
            
            // Check if token is not yet valid
            if (payload.nbf && payload.nbf > currentTime) {
                console.log('⏰ Token not yet valid. Nbf:', payload.nbf, 'Current:', currentTime);
                return false;
            }
            
            console.log('✅ Token validation successful');
            return true;
            
        } catch (error) {
            console.error('❌ Token validation failed:', error);
            return false;
        }
    }
    
    /**
     * Decode JWT token payload
     * @private
     * @param {string} token - JWT token
     * @returns {Object|null} Decoded payload or null
     */
    #decodeJWT(token) {
        try {
            console.log('🔍 Decoding JWT token:', token.substring(0, 20) + '...');
            
            const parts = token.split('.');
            if (parts.length !== 3) {
                console.log('❌ JWT has wrong number of parts:', parts.length);
                return null;
            }
            
            const payload = parts[1];
            console.log('🔍 JWT payload part (base64):', payload.substring(0, 20) + '...');
            
            // Use a more robust base64 decoding method
            const decoded = this.#base64Decode(payload);
            console.log('🔍 JWT payload decoded (raw):', decoded.substring(0, 100) + '...');
            
            const parsed = JSON.parse(decoded);
            console.log('🔍 JWT payload parsed:', parsed);
            return parsed;
            
        } catch (error) {
            console.error('❌ JWT decode failed:', error);
            return null;
        }
    }

    /**
     * Decode base64 string (handles URL-safe base64)
     * @private
     * @param {string} str - Base64 string
     * @returns {string} Decoded string
     */
    #base64Decode(str) {
        try {
            // Replace URL-safe characters
            str = str.replace(/-/g, '+').replace(/_/g, '/');
            
            // Add padding if needed
            while (str.length % 4) {
                str += '=';
            }
            
            // Use modern base64 decoding
            if (typeof window !== 'undefined' && window.atob) {
                return window.atob(str);
            } else if (typeof global !== 'undefined' && global.Buffer) {
                // Node.js environment
                return Buffer.from(str, 'base64').toString('utf8');
            } else {
                // Fallback for older browsers
                return atob(str);
            }
        } catch (error) {
            console.error('❌ Base64 decode failed:', error);
            throw error;
        }
    }
    
    /**
     * Restore user session from token
     * @private
     * @param {string} token - Valid JWT token
     */
    async #restoreSession(token) {
        try {
            const payload = this.#decodeJWT(token);
            if (!payload) {
                throw new Error('Invalid token payload');
            }
            
            // 🔍 DEBUG: Log the actual JWT payload to see what's in it
            console.log('🔍 JWT Payload decoded:', payload);
            console.log('🔍 Available fields:', Object.keys(payload));
            console.log('🔍 Username field:', payload.username);
            console.log('🔍 User ID field:', payload.user_id);
            console.log('🔍 Role field:', payload.role);
            
            // Extract user information from token
            this.#currentUser = {
                id: payload.sub || payload.user_id,
                username: payload.username || payload.preferred_username,
                email: payload.email,
                role: payload.role || 'user',
                permissions: payload.permissions || []
            };
            
            // 🔍 DEBUG: Log the extracted user information
            console.log('🔍 Extracted user info:', this.#currentUser);
            console.log('🔍 Username extracted:', this.#currentUser.username);
            console.log('🔍 User ID extracted:', this.#currentUser.id);
            console.log('🔍 Role extracted:', this.#currentUser.role);
            
            this.#userRole = this.#currentUser.role;
            this.#userPermissions = this.#currentUser.permissions;
            this.#isAuthenticated = true;
            this.#lastActivity = Date.now();
            
            // Store token
            this.#storeToken(token);
            
            // Dispatch auth state change event
            this.#dispatchAuthStateChange();
            
            console.log('✅ Session restored for user:', this.#currentUser.username);
            
        } catch (error) {
            console.error('❌ Session restoration failed:', error);
            this.#clearSession();
        }
    }
    
    /**
     * Store authentication token
     * @private
     * @param {string} token - JWT token to store
     */
    #storeToken(token) {
        try {
            // 🔍 DEBUG: Log token storage attempt
            console.log('🔍 storeToken called with token:', token ? `${token.substring(0, 20)}...` : 'null');
            console.log('🔍 currentUser state:', this.#currentUser);
            console.log('🔍 isAuthenticated state:', this.#isAuthenticated);
            
            // For demo users, store in sessionStorage (cleared on tab close)
            // For regular users, store in localStorage (persistent)
            // CRITICAL FIX: Handle case where currentUser is not set yet
            const isDemoUser = this.#currentUser?.username === 'demo';
            const storage = isDemoUser ? sessionStorage : localStorage;
            
            // CRITICAL FIX: Always store token, even if currentUser is not set yet
            // The token will be validated later when restoring the session
            storage.setItem(this.#config.storageKey, token);
            console.log('💾 Token stored in', isDemoUser ? 'sessionStorage' : 'localStorage');
            console.log('💾 Storage key used:', this.#config.storageKey);
            
        } catch (error) {
            console.error('❌ Token storage failed:', error);
        }
    }
    
    /**
     * Attempt automatic demo login
     * @private
     */
    async #attemptAutoDemoLogin() {
        try {
            console.log('🎭 Attempting auto-demo login...');
            
            // This will be implemented in SessionManager
            // For now, just log the attempt
            console.log('🎭 Auto-demo login requested');
            
        } catch (error) {
            console.warn('⚠️ Auto-demo login failed:', error);
        }
    }
    
    /**
     * Clear current authentication session
     * @private
     */
    #clearSession() {
        this.#isAuthenticated = false;
        this.#currentUser = null;
        this.#userRole = null;
        this.#userPermissions = [];
        this.#lastActivity = null;
        
        // Clear stored token
        try {
            sessionStorage.removeItem(this.#config.storageKey);
            localStorage.removeItem(this.#config.storageKey);
        } catch (error) {
            console.warn('⚠️ Could not clear stored token:', error);
        }
        
        // Dispatch auth state change event
        this.#dispatchAuthStateChange();
        
        console.log('🧹 Session cleared');
    }
    
    /**
     * Setup session monitoring
     * @private
     */
    #setupSessionMonitoring() {
        if (this.#sessionMonitor) {
            clearInterval(this.#sessionMonitor);
        }
        
        this.#sessionMonitor = setInterval(() => {
            this.#checkSessionValidity();
        }, 60000); // Check every minute
        
        console.log('⏰ Session monitoring started');
    }
    
    /**
     * Check session validity
     * @private
     */
    #checkSessionValidity() {
        if (!this.#isAuthenticated) {
            return;
        }
        
        const token = this.#getStoredToken();
        if (!token) {
            console.log('⏰ No token found, clearing session');
            this.#clearSession();
            return;
        }
        
        if (!this.#validateToken(token)) {
            console.log('⏰ Token invalid, clearing session');
            this.#clearSession();
            return;
        }
        
        // Check session timeout
        const sessionAge = Date.now() - this.#lastActivity;
        if (sessionAge > this.#config.sessionTimeout) {
            console.log('⏰ Session timeout, clearing session');
            this.#clearSession();
            return;
        }
    }
    
    /**
     * Setup activity monitoring
     * @private
     */
    #setupActivityMonitoring() {
        // Update last activity on user interaction
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        const updateActivity = () => {
            if (this.#isAuthenticated) {
                this.#lastActivity = Date.now();
            }
        };
        
        activityEvents.forEach(event => {
            document.addEventListener(event, updateActivity, { passive: true });
        });
        
        console.log('🖱️ Activity monitoring started');
    }
    
    /**
     * Dispatch authentication state change event
     * @private
     */
    #dispatchAuthStateChange() {
        const event = new CustomEvent('authStateChanged', {
            detail: {
                isAuthenticated: this.#isAuthenticated,
                user: this.#currentUser,
                role: this.#userRole,
                permissions: this.#userPermissions
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Auth state change event dispatched');
    }
    
    /**
     * Check if user is authenticated
     * @readonly
     * @returns {boolean} Authentication status
     */
    get isAuthenticated() {
        return this.#isAuthenticated;
    }
    
    /**
     * Get current authenticated user
     * @readonly
     * @returns {Object|null} User object or null
     */
    get currentUser() {
        return this.#currentUser;
    }
    
    /**
     * Get current user role
     * @readonly
     * @returns {string|null} User role or null
     */
    get userRole() {
        return this.#userRole;
    }
    
    /**
     * Get current user permissions
     * @readonly
     * @returns {Array} User permissions array
     */
    get userPermissions() {
        return [...this.#userPermissions];
    }
    
    /**
     * Check if user has specific permission
     * @param {string} permission - Permission to check
     * @returns {boolean} Has permission
     */
    hasPermission(permission) {
        if (!this.#isAuthenticated) {
            return false;
        }
        
        return this.#userPermissions.includes(permission);
    }
    
    /**
     * Check if user has specific role
     * @param {string} role - Role to check
     * @returns {boolean} Has role
     */
    hasRole(role) {
        if (!this.#isAuthenticated) {
            return false;
        }
        
        return this.#userRole === role;
    }
    
    /**
     * Get session information
     * @returns {Object} Session information
     */
    getSessionInfo() {
        return {
            isAuthenticated: this.#isAuthenticated,
            user: this.#currentUser,
            role: this.#userRole,
            permissions: this.#userPermissions,
            lastActivity: this.#lastActivity,
            sessionAge: this.#isAuthenticated ? Date.now() - this.#lastActivity : 0
        };
    }

    /**
     * Authenticate user with token (called by auth system after successful login)
     * @param {string} token - JWT token from successful login
     * @param {Object} userInfo - User information from login response
     */
    authenticateUser(token, userInfo) {
        try {
            console.log('🔐 AuthManager: Authenticating user with token and user info');
            console.log('🔍 User info received:', userInfo);
            console.log('🔍 Token received:', token ? `${token.substring(0, 20)}...` : 'null');
            
            // Store token first
            console.log('🔍 About to call #storeToken...');
            this.#storeToken(token);
            console.log('🔍 #storeToken completed');
            
            // Set user information
            this.#currentUser = {
                id: userInfo.user_id || userInfo.id,
                username: userInfo.username,
                email: userInfo.email,
                role: userInfo.role || 'user',
                permissions: userInfo.permissions || []
            };
            
            this.#userRole = this.#currentUser.role;
            this.#userPermissions = this.#currentUser.permissions;
            this.#isAuthenticated = true;
            this.#lastActivity = Date.now();
            
            // Dispatch auth state change event
            this.#dispatchAuthStateChange();
            
            console.log('✅ AuthManager: User authenticated successfully:', this.#currentUser.username);
            
        } catch (error) {
            console.error('❌ AuthManager: User authentication failed:', error);
            this.#clearSession();
            throw error;
        }
    }

    /**
     * Restore session from stored token (public method for auth system)
     * @param {string} token - JWT token to restore
     * @returns {Promise<boolean>} Success status
     */
    async restoreSessionFromToken(token) {
        try {
            console.log('🔐 AuthManager: Restoring session from token...');
            
            if (await this.#validateToken(token)) {
                await this.#restoreSession(token);
                console.log('✅ AuthManager: Session restored successfully');
                return true;
            } else {
                console.log('❌ AuthManager: Token validation failed');
                return false;
            }
            
        } catch (error) {
            console.error('❌ AuthManager: Session restoration failed:', error);
            return false;
        }
    }

    /**
     * Get stored authentication token
     * @returns {string|null} Stored token or null
     */
    getStoredToken() {
        try {
            // Use the private method to get the stored token
            return this.#getStoredToken();
        } catch (error) {
            console.warn('⚠️ Could not retrieve stored token:', error);
            return null;
        }
    }
    
    /**
     * Update user information
     * @param {Object} userInfo - New user information
     */
    updateUserInfo(userInfo) {
        if (!this.#isAuthenticated) {
            throw new Error('Cannot update user info: not authenticated');
        }
        
        this.#currentUser = { ...this.#currentUser, ...userInfo };
        this.#lastActivity = Date.now();
        
        // Dispatch auth state change event
        this.#dispatchAuthStateChange();
        
        console.log('✅ User info updated');
    }
    
    /**
     * Logout current user
     * @returns {Promise<boolean>} Success status
     */
    async logout() {
        try {
            console.log('🚪 Logging out user:', this.#currentUser?.username);
            
            this.#clearSession();
            
            // Stop monitoring
            if (this.#sessionMonitor) {
                clearInterval(this.#sessionMonitor);
                this.#sessionMonitor = null;
            }
            
            console.log('✅ Logout completed');
            return true;
            
        } catch (error) {
            console.error('❌ Logout failed:', error);
            return false;
        }
    }
    
    /**
     * Create a default AuthManager instance
     * @static
     * @returns {AuthManager} New instance with default config
     */
    static createDefault() {
        return new AuthManager({
            autoLogin: true,
            storageKey: 'auth_token',
            debug: false,
            sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
            activityTimeout: 30 * 60 * 1000 // 30 minutes
        });
    }
}
