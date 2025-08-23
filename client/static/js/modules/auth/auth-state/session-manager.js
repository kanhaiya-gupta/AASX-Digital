/**
 * Session Manager - Authentication Session Operations
 * @description Handles login, logout, and session management API calls
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-state/session-manager
 */

/**
 * Session Manager
 * @description Manages authentication sessions through API calls
 * @class SessionManager
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class SessionManager {
    // Private fields
    #isInitialized = false;
    #isAuthenticating = false;
    #currentSession = null;
    #loginAttempts = 0;
    #maxLoginAttempts = 5;
    #lockoutUntil = null;
    #config = {};
    #endpoints = {};
    #eventListeners = new Map();
    
    /**
     * Create a SessionManager instance
     * @param {Object} options - Configuration options
     * @param {string} options.baseURL - API base URL
     * @param {boolean} options.autoDemoLogin - Enable auto-demo login
     * @param {string} options.demoCredentials - Demo user credentials
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            baseURL: options.baseURL ?? '/api/auth',
            autoDemoLogin: options.autoDemoLogin ?? true,
            demoCredentials: options.demoCredentials ?? {
                username: 'demo',
                password: 'demo123'
            },
            debug: options.debug ?? false,
            lockoutDuration: options.lockoutDuration ?? 15 * 60 * 1000, // 15 minutes
            retryDelay: options.retryDelay ?? 1000 // 1 second
        };
        
        // API endpoints
        this.#endpoints = {
            login: `${this.#config.baseURL}/login`,
            logout: `${this.#config.baseURL}/logout`,
            refresh: `${this.#config.baseURL}/refresh`,
            config: `${this.#config.baseURL}/config`
        };
        
        console.log('🔐 SessionManager created with config:', this.#config);
    }
    
    /**
     * Initialize the session manager
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ SessionManager already initialized');
                return true;
            }
            
            console.log('🔐 Initializing SessionManager...');
            
            // Check API configuration
            await this.#checkAPIConfig();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            this.#isInitialized = true;
            console.log('✅ SessionManager initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ SessionManager initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Check API configuration and availability
     * @private
     */
    async #checkAPIConfig() {
        try {
            console.log('🔍 Checking API configuration...');
            
            const response = await fetch(this.#endpoints.config, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`API config check failed: ${response.status}`);
            }
            
            const config = await response.json();
            console.log('✅ API configuration loaded:', config);
            
        } catch (error) {
            console.warn('⚠️ API config check failed:', error);
            // Don't throw - we can still function with defaults
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    #setupEventListeners() {
        // Listen for auto-demo login requests
        window.addEventListener('requestAutoDemoLogin', (event) => {
            console.log('🎭 Auto-demo login requested via event');
            this.autoLoginAsDemo();
        });
        
        console.log('👂 Event listeners setup complete');
    }
    
    /**
     * Authenticate user with credentials
     * @param {Object} credentials - User credentials
     * @param {string} credentials.username - Username
     * @param {string} credentials.password - Password
     * @returns {Promise<Object>} Authentication result
     * @throws {Error} Authentication error
     */
    async authenticate(credentials) {
        try {
            // Check lockout status
            if (this.#isLockedOut()) {
                throw new Error('Account temporarily locked due to too many failed attempts');
            }
            
            // Validate credentials
            if (!credentials || !credentials.username || !credentials.password) {
                throw new Error('Invalid credentials provided');
            }
            
            console.log('🔐 Authenticating user:', credentials.username);
            
            // Check if already authenticating
            if (this.#isAuthenticating) {
                throw new Error('Authentication already in progress');
            }
            
            this.#isAuthenticating = true;
            
            // Make login API call
            const response = await fetch(this.#endpoints.login, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: credentials.username,
                    password: credentials.password
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Login failed: ${response.status}`);
            }
            
            const authData = await response.json();
            
            // Reset login attempts on success
            this.#loginAttempts = 0;
            this.#lockoutUntil = null;
            
            // Create session object
            this.#currentSession = {
                token: authData.access_token,
                refreshToken: authData.refresh_token,
                user: authData.user,
                expiresAt: authData.expires_at,
                createdAt: Date.now()
            };
            
            console.log('✅ Authentication successful for:', credentials.username);
            
            // Dispatch success event
            this.#dispatchAuthSuccess(authData);
            
            return {
                success: true,
                session: this.#currentSession,
                user: authData.user
            };
            
        } catch (error) {
            console.error('❌ Authentication failed:', error);
            
            // Increment failed attempts
            this.#loginAttempts++;
            
            // Check if should lockout
            if (this.#loginAttempts >= this.#maxLoginAttempts) {
                this.#lockoutUntil = Date.now() + this.#config.lockoutDuration;
                console.warn('🚫 Account locked until:', new Date(this.#lockoutUntil));
            }
            
            // Dispatch failure event
            this.#dispatchAuthFailure(error);
            
            throw error;
            
        } finally {
            this.#isAuthenticating = false;
        }
    }
    
    /**
     * Automatically login as demo user
     * @returns {Promise<Object>} Authentication result
     * @throws {Error} Auto-login error
     */
    async autoLoginAsDemo() {
        try {
            if (!this.#config.autoDemoLogin) {
                console.log('🎭 Auto-demo login disabled');
                return { success: false, reason: 'Auto-demo login disabled' };
            }
            
            console.log('🎭 Attempting auto-demo login...');
            
            // Check if already authenticated
            if (this.#currentSession) {
                console.log('🎭 Already authenticated, skipping auto-login');
                return { success: true, session: this.#currentSession };
            }
            
            // Attempt demo login
            const result = await this.authenticate(this.#config.demoCredentials);
            
            if (result.success) {
                console.log('🎭 Auto-demo login successful');
                
                // Dispatch auto-login event
                this.#dispatchAutoLoginSuccess(result);
                
                return result;
            }
            
        } catch (error) {
            console.warn('⚠️ Auto-demo login failed:', error);
            
            // Dispatch auto-login failure event
            this.#dispatchAutoLoginFailure(error);
            
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Logout current user
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Logout error
     */
    async logout() {
        try {
            if (!this.#currentSession) {
                console.log('🚪 No active session to logout');
                return true;
            }
            
            console.log('🚪 Logging out user...');
            
            // Call logout API
            try {
                const response = await fetch(this.#endpoints.logout, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.#currentSession.token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    console.warn('⚠️ Logout API call failed:', response.status);
                }
            } catch (error) {
                console.warn('⚠️ Logout API call failed:', error);
                // Continue with local logout even if API fails
            }
            
            // Clear local session
            this.#clearSession();
            
            // Reset login attempts
            this.#loginAttempts = 0;
            this.#lockoutUntil = null;
            
            console.log('✅ Logout completed');
            
            // Dispatch logout event
            this.#dispatchLogoutSuccess();
            
            return true;
            
        } catch (error) {
            console.error('❌ Logout failed:', error);
            throw error;
        }
    }
    
    /**
     * Refresh authentication token
     * @returns {Promise<Object>} Refresh result
     * @throws {Error} Refresh error
     */
    async refreshToken() {
        try {
            if (!this.#currentSession?.refreshToken) {
                throw new Error('No refresh token available');
            }
            
            console.log('🔄 Refreshing authentication token...');
            
            const response = await fetch(this.#endpoints.refresh, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.#currentSession.refreshToken
                })
            });
            
            if (!response.ok) {
                throw new Error(`Token refresh failed: ${response.status}`);
            }
            
            const refreshData = await response.json();
            
            // Update session with new token
            this.#currentSession = {
                ...this.#currentSession,
                token: refreshData.access_token,
                expiresAt: refreshData.expires_at,
                refreshedAt: Date.now()
            };
            
            console.log('✅ Token refreshed successfully');
            
            // Dispatch refresh event
            this.#dispatchTokenRefreshed(refreshData);
            
            return {
                success: true,
                session: this.#currentSession
            };
            
        } catch (error) {
            console.error('❌ Token refresh failed:', error);
            
            // Clear session on refresh failure
            this.#clearSession();
            
            throw error;
        }
    }
    
    /**
     * Check if account is locked out
     * @private
     * @returns {boolean} Lockout status
     */
    #isLockedOut() {
        if (!this.#lockoutUntil) {
            return false;
        }
        
        if (Date.now() < this.#lockoutUntil) {
            const remainingTime = Math.ceil((this.#lockoutUntil - Date.now()) / 1000 / 60);
            console.log(`🚫 Account locked for ${remainingTime} more minutes`);
            return true;
        }
        
        // Lockout expired
        this.#lockoutUntil = null;
        this.#loginAttempts = 0;
        return false;
    }
    
    /**
     * Clear current session
     * @private
     */
    #clearSession() {
        this.#currentSession = null;
        console.log('🧹 Session cleared');
    }
    
    /**
     * Dispatch authentication success event
     * @private
     * @param {Object} authData - Authentication data
     */
    #dispatchAuthSuccess(authData) {
        const event = new CustomEvent('authSuccess', {
            detail: {
                user: authData.user,
                session: this.#currentSession,
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Auth success event dispatched');
    }
    
    /**
     * Dispatch authentication failure event
     * @private
     * @param {Error} error - Authentication error
     */
    #dispatchAuthFailure(error) {
        const event = new CustomEvent('authFailure', {
            detail: {
                error: error.message,
                attempts: this.#loginAttempts,
                lockedOut: this.#isLockedOut(),
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Auth failure event dispatched');
    }
    
    /**
     * Dispatch auto-login success event
     * @private
     * @param {Object} result - Auto-login result
     */
    #dispatchAutoLoginSuccess(result) {
        const event = new CustomEvent('autoLoginSuccess', {
            detail: {
                user: result.user,
                session: result.session,
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Auto-login success event dispatched');
    }
    
    /**
     * Dispatch auto-login failure event
     * @private
     * @param {Error} error - Auto-login error
     */
    #dispatchAutoLoginFailure(error) {
        const event = new CustomEvent('autoLoginFailure', {
            detail: {
                error: error.message,
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Auto-login failure event dispatched');
    }
    
    /**
     * Dispatch logout success event
     * @private
     */
    #dispatchLogoutSuccess() {
        const event = new CustomEvent('logoutSuccess', {
            detail: {
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Logout success event dispatched');
    }
    
    /**
     * Dispatch token refreshed event
     * @private
     * @param {Object} refreshData - Token refresh data
     */
    #dispatchTokenRefreshed(refreshData) {
        const event = new CustomEvent('tokenRefreshed', {
            detail: {
                session: this.#currentSession,
                timestamp: Date.now()
            }
        });
        
        window.dispatchEvent(event);
        console.log('🔄 Token refreshed event dispatched');
    }
    
    /**
     * Get current session information
     * @readonly
     * @returns {Object|null} Current session or null
     */
    get currentSession() {
        return this.#currentSession;
    }
    
    /**
     * Check if user is authenticated
     * @readonly
     * @returns {boolean} Authentication status
     */
    get isAuthenticated() {
        return !!this.#currentSession;
    }
    
    /**
     * Check if authentication is in progress
     * @readonly
     * @returns {boolean} Authentication status
     */
    get isAuthenticating() {
        return this.#isAuthenticating;
    }
    
    /**
     * Get login attempt count
     * @readonly
     * @returns {number} Number of failed attempts
     */
    get loginAttempts() {
        return this.#loginAttempts;
    }
    
    /**
     * Check if account is locked out
     * @readonly
     * @returns {boolean} Lockout status
     */
    get isLockedOut() {
        return this.#isLockedOut();
    }
    
    /**
     * Get lockout remaining time
     * @readonly
     * @returns {number} Remaining lockout time in milliseconds
     */
    get lockoutRemainingTime() {
        if (!this.#lockoutUntil) {
            return 0;
        }
        
        const remaining = this.#lockoutUntil - Date.now();
        return remaining > 0 ? remaining : 0;
    }
    
    /**
     * Get session status information
     * @returns {Object} Session status
     */
    getSessionStatus() {
        return {
            isAuthenticated: this.isAuthenticated,
            isAuthenticating: this.isAuthenticating,
            currentSession: this.#currentSession,
            loginAttempts: this.#loginAttempts,
            isLockedOut: this.isLockedOut,
            lockoutRemainingTime: this.lockoutRemainingTime
        };
    }
    
    /**
     * Create a default SessionManager instance
     * @static
     * @returns {SessionManager} New instance with default config
     */
    static createDefault() {
        return new SessionManager({
            baseURL: '/api/auth',
            autoDemoLogin: true,
            demoCredentials: {
                username: 'demo',
                password: 'demo123'
            },
            debug: false,
            lockoutDuration: 15 * 60 * 1000, // 15 minutes
            retryDelay: 1000 // 1 second
        });
    }
}
