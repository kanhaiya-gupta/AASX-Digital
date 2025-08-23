/**
 * Analytics API Client for AASX-ETL Frontend
 * 
 * This service handles all API calls to the analytics endpoints
 * and provides data for the dashboard and analytics tabs.
 * 
 * Phase 5.2: Frontend Data Integration
 * 
 * IMPORTANT: This integrates with the CENTRAL AUTHENTICATION SYSTEM
 * for the user-based framework - no manual token handling needed.
 */

class AnalyticsAPI {
    constructor() {
        this.baseUrl = '/api/aasx-etl';
        this.analyticsUrl = `${this.baseUrl}/analytics`;
        this.isInitialized = false;
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
    }

    /**
     * Initialize the analytics service
     */
    async init() {
        try {
            console.log('🔄 Analytics Service: Starting initialization...');
            
            // Wait for global auth manager to be ready first
            await this.waitForAuthManager();
            
            // Update auth state
            this.updateAuthState();
            
            console.log('🔐 Analytics Service: Auth state after init:', {
                isAuthenticated: this.isAuthenticated,
                currentUser: this.currentUser
            });
            
            // Test connection to analytics health endpoint
            console.log('🏥 Analytics Service: Testing health endpoint...');
            const healthResponse = await this.makeRequest(`${this.analyticsUrl}/health`);
            
            if (healthResponse.success) {
                this.isInitialized = true;
                console.log('✅ Analytics service initialized successfully');
                return true;
            } else {
                throw new Error('Analytics service health check failed');
            }
        } catch (error) {
            console.error('❌ Failed to initialize analytics service:', error);
            this.isInitialized = false;
            return false;
        }
    }

    /**
     * Wait for global auth manager to be ready
     */
    async waitForAuthManager() {
        console.log('🔐 Analytics Service: Waiting for global auth manager...');
        
        // Wait for either authManager or CoreModule.authUI to be ready
        while (!window.authManager && !(window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI)) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Analytics Service: Global auth manager ready');
        
        // Initial auth state setup
        this.updateAuthState();
        
        // Listen for auth changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Analytics Service: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        window.addEventListener('logout', () => {
            console.log('🔐 Analytics Service: Logout detected');
            this.updateAuthState();
        });
    }

    /**
     * Update authentication state from global auth manager
     */
    updateAuthState() {
        try {
            let sessionInfo = null;
            
            // Try CoreModule.authUI first (newer system)
            if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
                sessionInfo = window.CoreModule.components.authUI.getAuthState();
                console.log('🔐 Analytics Service: Auth state update from CoreModule:', sessionInfo);
            }
            // Fallback to authManager (legacy system)
            else if (window.authManager) {
                sessionInfo = window.authManager.getSessionInfo();
                console.log('🔐 Analytics Service: Auth state update from authManager:', sessionInfo);
            }
            
            if (sessionInfo) {
                // Update local state based on auth manager
                this.isAuthenticated = sessionInfo.isAuthenticated;
                this.currentUser = sessionInfo.user || sessionInfo.currentUser;
            }
            
        } catch (error) {
            console.warn('⚠️ Analytics Service: Error updating auth state:', error);
        }
    }

    /**
     * Get current authentication state from global auth manager
     */
    getCurrentAuthState() {
        try {
            // Try CoreModule.authUI first (newer system)
            if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
                const state = window.CoreModule.components.authUI.getAuthState();
                console.log('🔐 Analytics Service: Got auth state from CoreModule:', state);
                return state;
            }
            
            // Try authSystemManager (legacy system)
            if (window.authSystemManager && window.authSystemManager.authManager) {
                const state = window.authSystemManager.authManager.getCurrentState();
                console.log('🔐 Analytics Service: Got auth state from authSystemManager:', state);
                return state;
            }
            
            // Fallback: check if we have a stored token
            const token = this.getStoredToken();
            if (token) {
                console.log('🔐 Analytics Service: Using fallback auth state (token exists)');
                return { isAuthenticated: true, user: { username: 'authenticated_user' } };
            }
            
            console.log('🔐 Analytics Service: No auth state available, defaulting to unauthenticated');
            return { isAuthenticated: false, user: null };
            
        } catch (error) {
            console.warn('⚠️ Analytics Service: Error getting auth state:', error);
            return { isAuthenticated: false, user: null };
        }
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Get current auth state and token
        const currentAuthState = this.getCurrentAuthState();
        const token = this.getStoredToken();
        
        if (token) {
            console.log(`🔐 Analytics Service: Auth token available - making authenticated request (User: ${currentAuthState.user?.username || 'Unknown'})`);
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.log(`🔐 Analytics Service: No auth token available - making unauthenticated request (Auth: ${currentAuthState.isAuthenticated ? 'Yes' : 'No'})`);
        }
        
        return headers;
    }

    /**
     * Get stored authentication token
     * @returns {string|null} Stored token or null
     */
    getStoredToken() {
        try {
            // Try CoreModule.authUI first (newer system)
            if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
                const authState = window.CoreModule.components.authUI.getAuthState();
                if (authState && authState.authToken) {
                    console.log('🔐 Analytics Service: Got token from CoreModule');
                    return authState.authToken;
                }
            }
            
            // Use the shared auth helper
            if (window.getAuthToken) {
                return window.getAuthToken();
            }
            
            // Fallback to direct storage access
            return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
        } catch (error) {
            console.warn('⚠️ Could not retrieve stored token:', error);
            return null;
        }
    }

    /**
     * Make authenticated API request using central auth system
     */
    async makeRequest(url, options = {}) {
        try {
            const defaultOptions = {
                method: 'GET',
                headers: this.getAuthHeaders(),
                ...options
            };

            console.log(`🌐 Analytics Service: Making API request to: ${url}`);
            console.log(`🔐 Analytics Service: Request headers:`, defaultOptions.headers);
            console.log(`🔐 Analytics Service: Auth state:`, this.getCurrentAuthState());

            const response = await fetch(url, defaultOptions);
            
            console.log(`📡 Analytics Service: Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ Analytics Service: API response received:`, data);
            return data;
        } catch (error) {
            console.error(`❌ API request failed for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Get dashboard overview data
     */
    async getDashboardOverview() {
        const cacheKey = 'dashboard_overview';
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/dashboard/overview`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get dashboard overview:', error);
            return this.getDefaultDashboardData();
        }
    }

    /**
     * Get dashboard summary cards data
     */
    async getDashboardSummaryCards() {
        const cacheKey = 'dashboard_summary_cards';
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/dashboard/summary-cards`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get dashboard summary cards:', error);
            return this.getDefaultSummaryCards();
        }
    }

    /**
     * Get recent processing jobs
     */
    async getRecentProcessingJobs(limit = 5) {
        const cacheKey = `recent_jobs_${limit}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/dashboard/recent-jobs?limit=${limit}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get recent processing jobs:', error);
            return { success: true, data: [], message: 'No recent jobs available' };
        }
    }

    /**
     * Get processing trends chart data
     */
    async getProcessingTrendsChart(days = 30) {
        const cacheKey = `processing_trends_${days}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/charts/processing-trends?days=${days}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get processing trends chart:', error);
            return this.getDefaultChartData();
        }
    }

    /**
     * Get quality metrics chart data
     */
    async getQualityMetricsChart(days = 30) {
        const cacheKey = `quality_metrics_${days}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/charts/quality-metrics?days=${days}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get quality metrics chart:', error);
            return this.getDefaultChartData();
        }
    }

    /**
     * Get performance metrics chart data
     */
    async getPerformanceMetricsChart(days = 30) {
        const cacheKey = `performance_metrics_${days}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/charts/performance-metrics?days=${days}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get performance metrics chart:', error);
            return this.getDefaultChartData();
        }
    }

    /**
     * Get user behavior chart data
     */
    async getUserBehaviorChart(days = 30) {
        const cacheKey = `user_behavior_${days}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/charts/user-behavior?days=${days}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get user behavior chart:', error);
            return this.getDefaultChartData();
        }
    }

    /**
     * Get dashboard metrics
     */
    async getDashboardMetrics() {
        const cacheKey = 'dashboard_metrics';
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/metrics/dashboard`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get dashboard metrics:', error);
            return this.getDefaultDashboardMetrics();
        }
    }

    /**
     * Get performance metrics
     */
    async getPerformanceMetrics(days = 30) {
        const cacheKey = `performance_metrics_${days}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        try {
            const data = await this.makeRequest(`${this.analyticsUrl}/metrics/performance?days=${days}`);
            this.setCachedData(cacheKey, data);
            return data;
        } catch (error) {
            console.error('❌ Failed to get performance metrics:', error);
            return this.getDefaultPerformanceMetrics();
        }
    }

    /**
     * Clear cache for specific key or all cache
     */
    clearCache(key = null) {
        if (key) {
            this.cache.delete(key);
            console.log(`🗑️ Cleared cache for: ${key}`);
        } else {
            this.cache.clear();
            console.log('🗑️ Cleared all analytics cache');
        }
    }

    /**
     * Refresh all data (clear cache and fetch fresh data)
     */
    async refreshAllData() {
        console.log('🔄 Refreshing all analytics data...');
        this.clearCache();
        
        // Trigger refresh of main dashboard
        const dashboardData = await this.getDashboardOverview();
        const summaryCards = await this.getDashboardSummaryCards();
        
        return {
            dashboard: dashboardData,
            summaryCards: summaryCards
        };
    }

    // Cache management methods
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    // Default data methods for fallback
    getDefaultDashboardData() {
        return {
            success: true,
            data: {
                summary_cards: this.getDefaultSummaryCards(),
                recent_activity: [],
                quick_stats: {
                    avg_processing_time: 0.0,
                    total_jobs_today: 0,
                    quality_score_avg: 0.0,
                    efficiency_score: 0.0
                },
                performance_indicators: {
                    success_rate_trend: 0.0,
                    processing_volume_trend: 0.0,
                    quality_trend: 0.0,
                    efficiency_trend: 0.0
                }
            },
            message: 'Using default dashboard data'
        };
    }

    getDefaultSummaryCards() {
        return [
            {
                title: 'Total Projects',
                value: 0,
                icon: 'fas fa-project-diagram',
                color: 'primary',
                trend: 0.0
            },
            {
                title: 'Total Files',
                value: 0,
                icon: 'fas fa-file-alt',
                color: 'info',
                trend: 0.0
            },
            {
                title: 'Processed Files',
                value: 0,
                icon: 'fas fa-check-circle',
                color: 'success',
                trend: 0.0
            },
            {
                title: 'Success Rate',
                value: '0.0%',
                icon: 'fas fa-chart-line',
                color: 'warning',
                trend: 0.0
            }
        ];
    }

    getDefaultChartData() {
        return {
            success: true,
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Data',
                        data: [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)'
                    }
                ]
            },
            message: 'Using default chart data'
        };
    }

    getDefaultDashboardMetrics() {
        return {
            success: true,
            data: {
                total_projects: 0,
                total_files: 0,
                processed_files: 0,
                success_rate: 0.0,
                processing_volume_trend: 0.0,
                error_rate: 0.0
            },
            message: 'Using default dashboard metrics'
        };
    }

    getDefaultPerformanceMetrics() {
        return {
            success: true,
            data: {
                avg_processing_time: 0.0,
                processing_efficiency_score: 0.0,
                quality_score_trend: 0.0,
                resource_utilization_trend: 0.0
            },
            message: 'Using default performance metrics'
        };
    }
}

// Export for use in other modules
window.AnalyticsAPI = AnalyticsAPI;
