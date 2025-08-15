/**
 * Authentication API Client - HTTP Operations
 * @description HTTP client for all authentication API operations
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-services/auth-api
 */

/**
 * Authentication API Client
 * @description Handles all HTTP operations for authentication
 * @class AuthAPI
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class AuthAPI {
    // Private fields
    #isInitialized = false;
    #isOnline = navigator.onLine;
    #pendingRequests = new Map();
    #requestQueue = [];
    #retryCount = 0;
    #config = {};
    #endpoints = {};
    #requestInterceptors = [];
    #responseInterceptors = [];
    #eventListeners = new Map();
    
    /**
     * Create an AuthAPI instance
     * @param {Object} options - Configuration options
     * @param {string} options.baseURL - API base URL
     * @param {number} options.timeout - Request timeout in milliseconds
     * @param {boolean} options.retryOnFailure - Enable retry on failure
     * @param {number} options.maxRetries - Maximum retry attempts
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            baseURL: options.baseURL ?? '/api/auth',
            timeout: options.timeout ?? 10000, // 10 seconds
            retryOnFailure: options.retryOnFailure ?? true,
            maxRetries: options.maxRetries ?? 3,
            debug: options.debug ?? false
        };
        
        // API endpoints
        this.#endpoints = {
            login: `${this.#config.baseURL}/login`,
            logout: `${this.#config.baseURL}/logout`,
            refresh: `${this.#config.baseURL}/refresh`,
            signup: `${this.#config.baseURL}/signup`,
            profile: `${this.#config.baseURL}/profile`,
            changePassword: `${this.#config.baseURL}/change-password`,
            permissions: `${this.#config.baseURL}/permissions`,
            config: `${this.#config.baseURL}/config`
        };
        
        console.log('🌐 AuthAPI created with config:', this.#config);
    }
    
    /**
     * Initialize the API client
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ AuthAPI already initialized');
                return true;
            }
            
            console.log('🌐 Initializing AuthAPI...');
            
            // Setup network monitoring
            this.#setupNetworkMonitoring();
            
            // Setup request/response interceptors
            this.#setupInterceptors();
            
            // Test API connectivity
            await this.#testConnectivity();
            
            this.#isInitialized = true;
            console.log('✅ AuthAPI initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ AuthAPI initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Setup network monitoring
     * @private
     */
    #setupNetworkMonitoring() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            this.#isOnline = true;
            console.log('🌐 Network connection restored');
            this.#processQueuedRequests();
        });
        
        window.addEventListener('offline', () => {
            this.#isOnline = false;
            console.log('🌐 Network connection lost');
        });
        
        console.log('📡 Network monitoring setup complete');
    }
    
    /**
     * Setup request/response interceptors
     * @private
     */
    #setupInterceptors() {
        // Default request interceptor - add auth token
        this.addRequestInterceptor(async (config) => {
            const token = this.#getAuthToken();
            if (token) {
                config.headers = config.headers || {};
                config.headers['Authorization'] = `Bearer ${token}`;
            }
            return config;
        });
        
        // Default response interceptor - handle common errors
        this.addResponseInterceptor(async (response) => {
            if (response.status === 401) {
                // Token expired or invalid
                this.#handleUnauthorized();
            } else if (response.status === 403) {
                // Insufficient permissions
                this.#handleForbidden();
            }
            return response;
        });
        
        console.log('🔗 Interceptors setup complete');
    }
    
    /**
     * Test API connectivity
     * @private
     */
    async #testConnectivity() {
        try {
            console.log('🔍 Testing API connectivity...');
            
            const response = await this.get(this.#endpoints.config);
            
            if (response.success) {
                console.log('✅ API connectivity confirmed');
            } else {
                throw new Error('API connectivity test failed');
            }
            
        } catch (error) {
            console.warn('⚠️ API connectivity test failed:', error);
            // Don't throw - we can still function with degraded mode
        }
    }
    
    /**
     * Add request interceptor
     * @param {Function} interceptor - Interceptor function
     */
    addRequestInterceptor(interceptor) {
        this.#requestInterceptors.push(interceptor);
    }
    
    /**
     * Add response interceptor
     * @param {Function} interceptor - Interceptor function
     */
    addResponseInterceptor(interceptor) {
        this.#responseInterceptors.push(interceptor);
    }
    
    /**
     * Execute request with interceptors
     * @private
     * @param {Object} config - Request configuration
     * @returns {Promise<Object>} Response
     */
    async #executeRequest(config) {
        try {
            // Apply request interceptors
            for (const interceptor of this.#requestInterceptors) {
                config = await interceptor(config);
            }
            
            // Check network status
            if (!this.#isOnline) {
                throw new Error('Network offline');
            }
            
            // Create request ID for tracking
            const requestId = this.#generateRequestId();
            this.#pendingRequests.set(requestId, config);
            
            // Execute request
            const response = await this.#makeRequest(config);
            
            // Apply response interceptors
            for (const interceptor of this.#responseInterceptors) {
                await interceptor(response);
            }
            
            // Remove from pending requests
            this.#pendingRequests.delete(requestId);
            
            return response;
            
        } catch (error) {
            console.error('❌ Request execution failed:', error);
            
            // Handle retry logic
            if (this.#config.retryOnFailure && this.#retryCount < this.#config.maxRetries) {
                return this.#retryRequest(config, error);
            }
            
            throw error;
        }
    }
    
    /**
     * Make HTTP request
     * @private
     * @param {Object} config - Request configuration
     * @returns {Promise<Object>} Response
     */
    async #makeRequest(config) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.#config.timeout);
        
        try {
            const response = await fetch(config.url, {
                method: config.method || 'GET',
                headers: config.headers || {},
                body: config.body,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // Parse response
            let data;
            try {
                data = await response.json();
            } catch {
                data = { message: response.statusText };
            }
            
            return {
                success: response.ok,
                status: response.status,
                statusText: response.statusText,
                data: data,
                headers: Object.fromEntries(response.headers.entries())
            };
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            
            throw error;
        }
    }
    
    /**
     * Retry failed request
     * @private
     * @param {Object} config - Request configuration
     * @param {Error} error - Original error
     * @returns {Promise<Object>} Response
     */
    async #retryRequest(config, error) {
        this.#retryCount++;
        console.log(`🔄 Retrying request (${this.#retryCount}/${this.#config.maxRetries})`);
        
        // Exponential backoff
        const delay = Math.pow(2, this.#retryCount) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        
        return this.#makeRequest(config);
    }
    
    /**
     * Generate unique request ID
     * @private
     * @returns {string} Request ID
     */
    #generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Get authentication token
     * @private
     * @returns {string|null} Auth token
     */
    #getAuthToken() {
        try {
            return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
        } catch (error) {
            return null;
        }
    }
    
    /**
     * Handle unauthorized response
     * @private
     */
    #handleUnauthorized() {
        console.log('🚫 Unauthorized - clearing auth state');
        
        // Dispatch unauthorized event
        const event = new CustomEvent('authUnauthorized', {
            detail: { timestamp: Date.now() }
        });
        
        window.dispatchEvent(event);
    }
    
    /**
     * Handle forbidden response
     * @private
     */
    #handleForbidden() {
        console.log('🚫 Forbidden - insufficient permissions');
        
        // Dispatch forbidden event
        const event = new CustomEvent('authForbidden', {
            detail: { timestamp: Date.now() }
        });
        
        window.dispatchEvent(event);
    }
    
    /**
     * Process queued requests
     * @private
     */
    async #processQueuedRequests() {
        if (this.#requestQueue.length === 0) return;
        
        console.log(`📤 Processing ${this.#requestQueue.length} queued requests`);
        
        const requests = [...this.#requestQueue];
        this.#requestQueue = [];
        
        for (const request of requests) {
            try {
                await this.#executeRequest(request.config);
                request.resolve();
            } catch (error) {
                request.reject(error);
            }
        }
    }
    
    /**
     * Queue request for later execution
     * @private
     * @param {Object} config - Request configuration
     * @returns {Promise<Object>} Response
     */
    #queueRequest(config) {
        return new Promise((resolve, reject) => {
            this.#requestQueue.push({ config, resolve, reject });
        });
    }
    
    /**
     * Make GET request
     * @param {string} url - Request URL
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response
     */
    async get(url, options = {}) {
        const config = {
            url: url,
            method: 'GET',
            headers: options.headers || {},
            ...options
        };
        
        if (!this.#isOnline) {
            return this.#queueRequest(config);
        }
        
        return this.#executeRequest(config);
    }
    
    /**
     * Make POST request
     * @param {string} url - Request URL
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response
     */
    async post(url, data = null, options = {}) {
        const config = {
            url: url,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: data ? JSON.stringify(data) : null,
            ...options
        };
        
        if (!this.#isOnline) {
            return this.#queueRequest(config);
        }
        
        return this.#executeRequest(config);
    }
    
    /**
     * Make PUT request
     * @param {string} url - Request URL
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response
     */
    async put(url, data = null, options = {}) {
        const config = {
            url: url,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: data ? JSON.stringify(data) : null,
            ...options
        };
        
        if (!this.#isOnline) {
            return this.#queueRequest(config);
        }
        
        return this.#executeRequest(config);
    }
    
    /**
     * Make DELETE request
     * @param {string} url - Request URL
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response
     */
    async delete(url, options = {}) {
        const config = {
            url: url,
            method: 'DELETE',
            headers: options.headers || {},
            ...options
        };
        
        if (!this.#isOnline) {
            return this.#queueRequest(config);
        }
        
        return this.#executeRequest(config);
    }
    
    /**
     * Login user
     * @param {Object} credentials - User credentials
     * @returns {Promise<Object>} Login response
     */
    async login(credentials) {
        return this.post(this.#endpoints.login, credentials);
    }
    
    /**
     * Logout user
     * @returns {Promise<Object>} Logout response
     */
    async logout() {
        return this.post(this.#endpoints.logout);
    }
    
    /**
     * Refresh token
     * @param {string} refreshToken - Refresh token
     * @returns {Promise<Object>} Refresh response
     */
    async refreshToken(refreshToken) {
        return this.post(this.#endpoints.refresh, { refresh_token: refreshToken });
    }
    
    /**
     * Signup user
     * @param {Object} userData - User registration data
     * @returns {Promise<Object>} Signup response
     */
    async signup(userData) {
        return this.post(this.#endpoints.signup, userData);
    }
    
    /**
     * Get user profile
     * @returns {Promise<Object>} Profile response
     */
    async getProfile() {
        return this.get(this.#endpoints.profile);
    }
    
    /**
     * Update user profile
     * @param {Object} profileData - Profile data to update
     * @returns {Promise<Object>} Update response
     */
    async updateProfile(profileData) {
        return this.put(this.#endpoints.profile, profileData);
    }
    
    /**
     * Change password
     * @param {Object} passwordData - Password change data
     * @returns {Promise<Object>} Password change response
     */
    async changePassword(passwordData) {
        return this.post(this.#endpoints.changePassword, passwordData);
    }
    
    /**
     * Get user permissions
     * @returns {Promise<Object>} Permissions response
     */
    async getPermissions() {
        return this.get(this.#endpoints.permissions);
    }
    
    /**
     * Get API configuration
     * @returns {Promise<Object>} Config response
     */
    async getConfig() {
        return this.get(this.#endpoints.config);
    }
    
    /**
     * Check if API is online
     * @readonly
     * @returns {boolean} Online status
     */
    get isOnline() {
        return this.#isOnline;
    }
    
    /**
     * Get pending request count
     * @readonly
     * @returns {number} Pending request count
     */
    get pendingRequestCount() {
        return this.#pendingRequests.size;
    }
    
    /**
     * Get queued request count
     * @readonly
     * @returns {number} Queued request count
     */
    get queuedRequestCount() {
        return this.#requestQueue.length;
    }
    
    /**
     * Get retry count
     * @readonly
     * @returns {number} Current retry count
     */
    get retryCount() {
        return this.#retryCount;
    }
    
    /**
     * Get API status information
     * @returns {Object} API status
     */
    getAPIStatus() {
        return {
            isOnline: this.isOnline,
            isInitialized: this.#isInitialized,
            pendingRequests: this.pendingRequestCount,
            queuedRequests: this.queuedRequestCount,
            retryCount: this.retryCount,
            endpoints: this.#endpoints
        };
    }
    
    /**
     * Create a default AuthAPI instance
     * @static
     * @returns {AuthAPI} New instance with default config
     */
    static createDefault() {
        return new AuthAPI({
            baseURL: '/api/auth',
            timeout: 10000,
            retryOnFailure: true,
            maxRetries: 3,
            debug: false
        });
    }
}
