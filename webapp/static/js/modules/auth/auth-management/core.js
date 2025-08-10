/**
 * Authentication Core Module
 * Handles core authentication functionality, session management, and user state
 * CACHE BUST: 2025-08-10-20:45
 */

export default class AuthCore {
    constructor() {
        this.isInitialized = false;
        this.currentUser = null;
        this.sessionToken = null;
        this.isAuthenticated = false;
        this.sessionTimeout = null;
        this.autoRefreshInterval = null;
        this.config = {
            sessionTimeoutMinutes: 30,
            autoRefreshIntervalMinutes: 5,
            apiBaseUrl: '/api/auth',
            endpoints: {
                login: '/login',
                logout: '/logout',
                register: '/register',
                profile: '/profile',
                refresh: '/refresh',
                validate: '/validate',
                changePassword: '/change-password',
                resetPassword: '/reset-password',
                verifyEmail: '/verify-email'
            }
        };
    }

    /**
     * Initialize Authentication Core
     */
    async init() {
        console.log('🔐 Initializing Authentication Core...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Check for existing session
            await this.checkExistingSession();

            // Setup session monitoring
            this.setupSessionMonitoring();

            // Setup auto-refresh
            this.setupAutoRefresh();

            this.isInitialized = true;
            console.log('✅ Authentication Core initialized');

        } catch (error) {
            console.error('❌ Authentication Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load authentication configuration
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('⚠️ Could not load auth config, using defaults:', error);
        }
    }

    /**
     * Check for existing session
     */
    async checkExistingSession() {
        // For now, always start in unauthenticated state to prevent tab switching
        console.log('🔐 Starting in unauthenticated state to prevent automatic tab switching');
        this.isAuthenticated = false;
        this.sessionToken = null;
        
        // Clear any stored tokens to ensure clean state
        this.clearStoredToken();
        
        // Comment out the original logic for now
        /*
        const token = this.getStoredToken();
        if (token) {
            try {
                const isValid = await this.validateToken(token);
                if (isValid) {
                    this.sessionToken = token;
                    this.isAuthenticated = true;
                    // Don't automatically load user profile to prevent tab switching
                    // await this.loadUserProfile();
                    console.log('🔑 Existing session restored (profile loading deferred)');
                } else {
                    this.clearStoredToken();
                }
            } catch (error) {
                console.warn('⚠️ Session validation failed:', error);
                this.clearStoredToken();
            }
        }
        */
    }

    /**
     * Setup session monitoring
     */
    setupSessionMonitoring() {
        // Monitor user activity
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        
        const resetSessionTimeout = () => {
            if (this.sessionTimeout) {
                clearTimeout(this.sessionTimeout);
            }
            
            this.sessionTimeout = setTimeout(() => {
                this.handleSessionTimeout();
            }, this.config.sessionTimeoutMinutes * 60 * 1000);
        };

        activityEvents.forEach(event => {
            document.addEventListener(event, resetSessionTimeout, true);
        });

        // Initial timeout setup
        resetSessionTimeout();
    }

    /**
     * Setup auto-refresh token
     */
    setupAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }

        this.autoRefreshInterval = setInterval(async () => {
            if (this.isAuthenticated && this.sessionToken) {
                try {
                    await this.refreshToken();
                } catch (error) {
                    console.warn('⚠️ Token refresh failed:', error);
                }
            }
        }, this.config.autoRefreshIntervalMinutes * 60 * 1000);
    }

    /**
     * Handle session timeout
     */
    async handleSessionTimeout() {
        console.log('⏰ Session timeout detected');
        await this.logout('Session expired due to inactivity');
    }

    /**
     * Login user
     * @param {string} username - Username or email
     * @param {string} password - Password
     * @param {boolean} rememberMe - Remember login
     * @returns {Object} Login result
     */
    async login(username, password, rememberMe = false) {
        try {
            console.log('🔐 Attempting login...');

            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.login}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password,
                    remember_me: rememberMe
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.sessionToken = data.access_token || data.token;
                this.isAuthenticated = true;
                this.currentUser = data.user;

                // Store token
                this.storeToken(this.sessionToken, rememberMe);

                // Load user profile
                await this.loadUserProfile();

                // Check for password expiration warning
                if (data.password_expiration) {
                    const expiration = data.password_expiration;
                    if (expiration.expired) {
                        console.warn('⚠️ Password has expired');
                        return { 
                            success: true, 
                            user: data.user, 
                            passwordExpired: true,
                            passwordExpiration: expiration
                        };
                    } else if (expiration.days_remaining <= 7) {
                        console.warn(`⚠️ Password expires in ${expiration.days_remaining} days`);
                        return { 
                            success: true, 
                            user: data.user, 
                            passwordExpiringSoon: true,
                            passwordExpiration: expiration
                        };
                    }
                }

                console.log('✅ Login successful');
                return { success: true, user: data.user };
            } else {
                console.error('❌ Login failed:', data.message);
                return { success: false, error: data.message };
            }

        } catch (error) {
            console.error('❌ Login error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Logout user
     * @param {string} reason - Logout reason
     */
    async logout(reason = 'User logout') {
        try {
            if (this.sessionToken) {
                await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.logout}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.sessionToken}`
                    }
                });
            }
        } catch (error) {
            console.warn('⚠️ Logout request failed:', error);
        } finally {
            this.clearSession();
            console.log('👋 Logged out:', reason);
        }
    }

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Object} Registration result
     */
    async register(userData) {
        try {
            console.log('📝 Attempting registration...');

            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.register}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                console.log('✅ Registration successful');
                return { success: true, user: data.user };
            } else {
                console.error('❌ Registration failed:', data.message);
                return { success: false, error: data.message };
            }

        } catch (error) {
            console.error('❌ Registration error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Load user profile
     */
    async loadUserProfile() {
        if (!this.sessionToken) return;

        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.profile}`, {
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`
                }
            });

            if (response.ok) {
                const profile = await response.json();
                this.currentUser = { ...this.currentUser, ...profile };
            }
        } catch (error) {
            console.warn('⚠️ Failed to load user profile:', error);
        }
    }

    /**
     * Validate token
     * @param {string} token - Token to validate
     * @returns {boolean} Token validity
     */
    async validateToken(token) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.validate}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            return response.ok;
        } catch (error) {
            console.warn('⚠️ Token validation failed:', error);
            return false;
        }
    }

    /**
     * Refresh token
     */
    async refreshToken() {
        if (!this.sessionToken) return;

        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.refresh}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.sessionToken = data.token;
                this.storeToken(data.token, false);
                console.log('🔄 Token refreshed');
            }
        } catch (error) {
            console.warn('⚠️ Token refresh failed:', error);
            throw error;
        }
    }

    /**
     * Change password
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @returns {Object} Result
     */
    async changePassword(currentPassword, newPassword) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.changePassword}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.sessionToken}`
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                console.log('✅ Password changed successfully');
                return { success: true };
            } else {
                console.error('❌ Password change failed:', data.message);
                return { success: false, error: data.message };
            }

        } catch (error) {
            console.error('❌ Password change error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Reset password
     * @param {string} email - User email
     * @returns {Object} Result
     */
    async resetPassword(email) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.resetPassword}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (response.ok) {
                console.log('✅ Password reset email sent');
                return { success: true };
            } else {
                console.error('❌ Password reset failed:', data.message);
                return { success: false, error: data.message };
            }

        } catch (error) {
            console.error('❌ Password reset error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Verify email
     * @param {string} token - Verification token
     * @returns {Object} Result
     */
    async verifyEmail(token) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.verifyEmail}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });

            const data = await response.json();

            if (response.ok) {
                console.log('✅ Email verified successfully');
                return { success: true };
            } else {
                console.error('❌ Email verification failed:', data.message);
                return { success: false, error: data.message };
            }

        } catch (error) {
            console.error('❌ Email verification error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Store token in storage
     * @param {string} token - Token to store
     * @param {boolean} rememberMe - Whether to remember login
     */
    storeToken(token, rememberMe) {
        const storage = rememberMe ? localStorage : sessionStorage;
        storage.setItem('auth_token', token);
    }

    /**
     * Get stored token
     * @returns {string|null} Stored token
     */
    getStoredToken() {
        return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    }

    /**
     * Clear stored token
     */
    clearStoredToken() {
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_token');
    }

    /**
     * Clear session data
     */
    clearSession() {
        this.sessionToken = null;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.clearStoredToken();

        if (this.sessionTimeout) {
            clearTimeout(this.sessionTimeout);
            this.sessionTimeout = null;
        }
    }

    /**
     * Get current user
     * @returns {Object|null} Current user
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isUserAuthenticated() {
        return this.isAuthenticated && this.sessionToken !== null;
    }

    /**
     * Get session token
     * @returns {string|null} Session token
     */
    getSessionToken() {
        return this.sessionToken;
    }

    /**
     * Get authentication configuration
     * @returns {Object} Configuration
     */
    getConfiguration() {
        return this.config;
    }

    /**
     * Refresh authentication data
     */
    async refreshData() {
        if (this.isAuthenticated) {
            await this.loadUserProfile();
        }
    }

    /**
     * Destroy authentication core
     */
    destroy() {
        if (this.sessionTimeout) {
            clearTimeout(this.sessionTimeout);
        }

        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }

        this.isInitialized = false;
        console.log('🧹 Authentication Core destroyed');
    }
    
    /**
     * Get AuthUIManager instance
     */
    async getAuthUIManager() {
        try {
            // Import AuthUIManager dynamically
            const { AuthUIManager } = await import('./auth-ui-manager.js');
            return new AuthUIManager();
        } catch (error) {
            console.error('❌ Failed to get AuthUIManager:', error);
            return null;
        }
    }
} 