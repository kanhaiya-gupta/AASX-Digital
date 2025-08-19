/**
 * Twin Registry Analytics Dashboard Module
 * Handles analytics dashboard functionality with central authentication integration
 */

export default class TwinRegistryAnalytics {
    constructor() {
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        this.analyticsData = {
            overview: {},
            trends: [],
            distributions: {},
            insights: []
        };
        
        // Analytics specific element IDs
        this.elementIds = {
            overviewCards: 'twin_registry_analyticsOverview',
            trendsChart: 'twin_registry_trendsChart',
            distributionChart: 'twin_registry_distributionChart',
            insightsContainer: 'twin_registry_insightsContainer',
            refreshBtn: 'twin_registry_analyticsRefreshBtn',
            exportBtn: 'twin_registry_analyticsExportBtn'
        };
        
        this.charts = {};
        this.refreshInterval = null;
    }

    /**
     * Initialize Analytics Dashboard
     */
    async init() {
        console.log('📊 Initializing Twin Registry Analytics Dashboard...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial analytics data
            await this.loadAnalyticsData();
            
            // Initialize charts
            this.initializeCharts();
            
            // Setup auto-refresh
            this.setupAutoRefresh();
            
            this.isInitialized = true;
            console.log('✅ Twin Registry Analytics Dashboard initialized');
            
        } catch (error) {
            console.error('❌ Twin Registry Analytics Dashboard initialization failed:', error);
            throw error;
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry Analytics: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry Analytics: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry Analytics: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Twin Registry Analytics: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ Twin Registry Analytics: No auth manager available');
            return;
        }
        
        try {
            // Check if new auth system is available
            if (typeof window.authManager.getSessionInfo === 'function') {
                const sessionInfo = window.authManager.getSessionInfo();
                console.log('🔐 Twin Registry Analytics: Auth state update (new system):', sessionInfo);
                
                if (sessionInfo && sessionInfo.isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: sessionInfo.user_id,
                        username: sessionInfo.username,
                        role: sessionInfo.role,
                        organization_id: sessionInfo.organization_id
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Analytics: User authenticated:', this.currentUser.username);
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Analytics: User not authenticated');
                }
            } else if (typeof window.authManager.isAuthenticated === 'function') {
                // Fallback to old auth system
                const isAuthenticated = window.authManager.isAuthenticated();
                console.log('🔐 Twin Registry Analytics: Auth state update (old system):', isAuthenticated);
                
                if (isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: 'unknown',
                        username: 'authenticated_user',
                        role: 'user',
                        organization_id: 'unknown'
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Analytics: User authenticated (legacy)');
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Analytics: User not authenticated (legacy)');
                }
            } else {
                console.log('⚠️ Twin Registry Analytics: Unknown auth manager API');
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
            }
        } catch (error) {
            console.warn('⚠️ Twin Registry Analytics: Error updating auth state:', error);
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
        }
    }

    /**
     * Setup authentication listeners
     */
    setupAuthListeners() {
        // Listen for auth state changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Twin Registry Analytics: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 Twin Registry Analytics: Login success detected');
            this.updateAuthState();
            await this.handleLoginSuccess();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 Twin Registry Analytics: Logout detected');
            this.updateAuthState();
            this.handleLogout();
        });
    }

    /**
     * Handle login success
     */
    async handleLoginSuccess() {
        try {
            await this.loadAnalyticsData();
            this.initializeCharts();
            console.log('✅ Twin Registry Analytics: User data refreshed after login');
        } catch (error) {
            console.error('❌ Twin Registry Analytics: Failed to refresh user data after login:', error);
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        this.analyticsData = {
            overview: {},
            trends: [],
            distributions: {},
            insights: []
        };
        this.currentUser = null;
        this.isAuthenticated = false;
        this.clearCharts();
        console.log('🔐 Twin Registry Analytics: User data cleared after logout');
    }

    /**
     * Handle auth state change
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.currentUser) {
            this.showAuthenticatedFeatures();
        } else {
            this.showDemoMode();
        }
    }

    /**
     * Show authenticated user features
     */
    showAuthenticatedFeatures() {
        console.log('🔐 Twin Registry Analytics: Showing authenticated user features');
        // Enable full analytics functionality
    }

    /**
     * Show demo mode
     */
    showDemoMode() {
        console.log('🔐 Twin Registry Analytics: Showing demo mode');
        // Show limited demo functionality
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById(this.elementIds.refreshBtn);
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAnalyticsData());
        }

        // Export button
        const exportBtn = document.getElementById(this.elementIds.exportBtn);
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportAnalyticsData());
        }

        // Listen for custom refresh events
        window.addEventListener('twinRegistryRefresh', () => {
            this.loadAnalyticsData();
        });
    }

    /**
     * Load analytics data
     */
    async loadAnalyticsData() {
        try {
            console.log('📊 Loading analytics data...');
            this.showLoading();
            
            // Load overview data
            await this.loadOverviewData();
            
            // Load trends data
            await this.loadTrendsData();
            
            // Load distribution data
            await this.loadDistributionData();
            
            // Load insights
            await this.loadInsights();
            
            // Update UI
            this.updateAnalyticsDisplay();
            
            this.hideLoading();
            console.log('✅ Analytics data loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load analytics data:', error);
            this.hideLoading();
            this.showError('Failed to load analytics data. Please try again.');
        }
    }
    
    /**
     * Update analytics UI with loaded data (for tab switching)
     */
    async updateAnalyticsUI() {
        try {
            console.log('📈 Updating analytics UI for tab switching...');
            
            // Update analytics dashboard elements
            if (this.analyticsData) {
                const data = this.analyticsData;
                
                // Update overview metrics
                const totalTwinsElement = document.getElementById('twin_registry_analytics_totalTwins');
                if (totalTwinsElement) totalTwinsElement.textContent = data.totalTwins;
                
                // Update charts if they exist
                if (window.twinRegistryChartUpdater) {
                    window.twinRegistryChartUpdater.updateAnalyticsCharts(data);
                }
            }
            
            console.log('✅ Analytics UI updated');
            
        } catch (error) {
            console.error('❌ Failed to update analytics UI:', error);
        }
    }
    
    /**
     * Load analytics data for UI display (simplified version for tab switching)
     */
    async loadAnalyticsData() {
        try {
            console.log('📈 Loading analytics data for tab switching...');
            
            // Get twins data to calculate analytics
            const response = await fetch('/api/twin-registry/twins', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                const twins = data.twins || [];
                
                // Calculate analytics metrics
                const analyticsData = {
                    totalTwins: twins.length,
                    twinTypes: this.calculateTwinTypeDistribution(twins),
                    healthDistribution: this.calculateHealthDistribution(twins),
                    lifecyclePhases: this.calculateLifecycleDistribution(twins),
                    integrationStatus: this.calculateIntegrationStatusDistribution(twins)
                };
                
                this.analyticsData = analyticsData;
                
                console.log('✅ Analytics data loaded:', analyticsData);
            }
            
        } catch (error) {
            console.error('❌ Failed to load analytics data:', error);
        }
    }
    
    /**
     * Update analytics UI with loaded data (for tab switching)
     */
    async updateAnalyticsUI() {
        try {
            console.log('📈 Updating analytics UI for tab switching...');
            
            // Update analytics dashboard elements
            if (this.analyticsData) {
                const data = this.analyticsData;
                
                // Update overview metrics
                const totalTwinsElement = document.getElementById('twin_registry_analytics_totalTwins');
                if (totalTwinsElement) totalTwinsElement.textContent = data.totalTwins;
                
                // Update charts if they exist
                if (window.twinRegistryChartUpdater) {
                    window.twinRegistryChartUpdater.updateAnalyticsCharts(data);
                }
            }
            
            console.log('✅ Analytics UI updated');
            
        } catch (error) {
            console.error('❌ Failed to update analytics UI:', error);
        }
    }

    /**
     * Load overview data
     */
    async loadOverviewData() {
        try {
            const response = await fetch('/api/twin-registry/analytics/overview', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.analyticsData.overview = data;
            }
        } catch (error) {
            console.error('❌ Failed to load overview data:', error);
        }
    }

    /**
     * Load trends data
     */
    async loadTrendsData() {
        try {
            const response = await fetch('/api/twin-registry/analytics/trends', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.analyticsData.trends = data.trends || [];
            }
        } catch (error) {
            console.error('❌ Failed to load trends data:', error);
        }
    }

    /**
     * Load distribution data
     */
    async loadDistributionData() {
        try {
            const response = await fetch('/api/twin-registry/analytics/distributions', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.analyticsData.distributions = data;
            }
        } catch (error) {
            console.error('❌ Failed to load distribution data:', error);
        }
    }

    /**
     * Load insights
     */
    async loadInsights() {
        try {
            const response = await fetch('/api/twin-registry/analytics/insights', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.analyticsData.insights = data.insights || [];
            }
        } catch (error) {
            console.error('❌ Failed to load insights:', error);
        }
    }

    /**
     * Initialize charts
     */
    initializeCharts() {
        try {
            // Initialize trends chart
            this.initializeTrendsChart();
            
            // Initialize distribution chart
            this.initializeDistributionChart();
            
            console.log('✅ Analytics charts initialized');
        } catch (error) {
            console.error('❌ Failed to initialize charts:', error);
        }
    }

    /**
     * Initialize trends chart
     */
    initializeTrendsChart() {
        const chartElement = document.getElementById(this.elementIds.trendsChart);
        if (!chartElement) return;

        // Create Chart.js chart for trends
        this.charts.trends = new Chart(chartElement, {
            type: 'line',
            data: {
                labels: this.analyticsData.trends.map(t => t.date),
                datasets: [{
                    label: 'Twin Health Score',
                    data: this.analyticsData.trends.map(t => t.health_score),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Twin Health Trends'
                    }
                }
            }
        });
    }

    /**
     * Initialize distribution chart
     */
    initializeDistributionChart() {
        const chartElement = document.getElementById(this.elementIds.distributionChart);
        if (!chartElement) return;

        // Create Chart.js chart for distributions
        this.charts.distribution = new Chart(chartElement, {
            type: 'doughnut',
            data: {
                labels: ['Healthy', 'Warning', 'Critical'],
                datasets: [{
                    data: [
                        this.analyticsData.distributions.healthy || 0,
                        this.analyticsData.distributions.warning || 0,
                        this.analyticsData.distributions.critical || 0
                    ],
                    backgroundColor: [
                        'rgb(75, 192, 192)',
                        'rgb(255, 205, 86)',
                        'rgb(255, 99, 132)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Twin Health Distribution'
                    }
                }
            }
        });
    }

    /**
     * Update analytics display
     */
    updateAnalyticsDisplay() {
        this.updateOverviewCards();
        this.updateInsights();
        this.updateCharts();
    }

    /**
     * Update overview cards
     */
    updateOverviewCards() {
        const container = document.getElementById(this.elementIds.overviewCards);
        if (!container) return;

        const overview = this.analyticsData.overview;
        
        // Update overview statistics
        this.updateElement('twin_registry_analyticsTotalTwins', overview.total_twins || 0);
        this.updateElement('twin_registry_analyticsHealthyTwins', overview.healthy_twins || 0);
        this.updateElement('twin_registry_analyticsWarningTwins', overview.warning_twins || 0);
        this.updateElement('twin_registry_analyticsCriticalTwins', overview.critical_twins || 0);
    }

    /**
     * Update insights
     */
    updateInsights() {
        const container = document.getElementById(this.elementIds.insightsContainer);
        if (!container) return;

        const insights = this.analyticsData.insights;
        
        if (insights.length === 0) {
            container.innerHTML = '<p class="text-muted">No insights available</p>';
            return;
        }

        const insightsHtml = insights.map(insight => `
            <div class="tr-insight-card">
                <div class="tr-insight-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <div class="tr-insight-content">
                    <h6>${insight.title}</h6>
                    <p>${insight.description}</p>
                    <small class="text-muted">${insight.timestamp}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = insightsHtml;
    }

    /**
     * Update charts
     */
    updateCharts() {
        if (this.charts.trends) {
            this.charts.trends.data.labels = this.analyticsData.trends.map(t => t.date);
            this.charts.trends.data.datasets[0].data = this.analyticsData.trends.map(t => t.health_score);
            this.charts.trends.update();
        }

        if (this.charts.distribution) {
            this.charts.distribution.data.datasets[0].data = [
                this.analyticsData.distributions.healthy || 0,
                this.analyticsData.distributions.warning || 0,
                this.analyticsData.distributions.critical || 0
            ];
            this.charts.distribution.update();
        }
    }

    /**
     * Update element by ID
     */
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Export analytics data
     */
    exportAnalyticsData() {
        try {
            const dataStr = JSON.stringify(this.analyticsData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'twin-registry-analytics.json';
            link.click();
            
            URL.revokeObjectURL(url);
            console.log('📊 Analytics data exported successfully');
        } catch (error) {
            console.error('❌ Failed to export analytics data:', error);
            this.showError('Failed to export analytics data');
        }
    }
    
    /**
     * Load analytics data for UI display
     */
    async loadAnalyticsData() {
        try {
            console.log('📈 Loading analytics data...');
            
            // Get twins data to calculate analytics
            const response = await fetch('/api/twin-registry/twins', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                const twins = data.twins || [];
                
                // Calculate analytics metrics
                const analyticsData = {
                    totalTwins: twins.length,
                    twinTypes: this.calculateTwinTypeDistribution(twins),
                    healthDistribution: this.calculateHealthDistribution(twins),
                    lifecyclePhases: this.calculateLifecycleDistribution(twins),
                    integrationStatus: this.calculateIntegrationStatusDistribution(twins)
                };
                
                this.analyticsData = analyticsData;
                
                console.log('✅ Analytics data loaded:', analyticsData);
            }
            
        } catch (error) {
            console.error('❌ Failed to load analytics data:', error);
        }
    }
    
    /**
     * Update analytics UI with loaded data
     */
    async updateAnalyticsUI() {
        try {
            console.log('📈 Updating analytics UI...');
            
            // Update analytics dashboard elements
            if (this.analyticsData) {
                const data = this.analyticsData;
                
                // Update overview metrics
                const totalTwinsElement = document.getElementById('twin_registry_analytics_totalTwins');
                if (totalTwinsElement) totalTwinsElement.textContent = data.totalTwins;
                
                // Update charts if they exist
                if (window.twinRegistryChartUpdater) {
                    window.twinRegistryChartUpdater.updateAnalyticsCharts(data);
                }
            }
            
            console.log('✅ Analytics UI updated');
            
        } catch (error) {
            console.error('❌ Failed to update analytics UI:', error);
        }
    }
    
    /**
     * Calculate twin type distribution
     */
    calculateTwinTypeDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const type = twin.twin_type || 'Unknown';
            distribution[type] = (distribution[type] || 0) + 1;
        });
        return distribution;
    }
    
    /**
     * Calculate health distribution
     */
    calculateHealthDistribution(twins) {
        const distribution = {
            excellent: twins.filter(t => (t.overall_health_score || 0) >= 90).length,
            good: twins.filter(t => (t.overall_health_score || 0) >= 75 && (t.overall_health_score || 0) < 90).length,
            warning: twins.filter(t => (t.overall_health_score || 0) >= 60 && (t.overall_health_score || 0) < 75).length,
            critical: twins.filter(t => (t.overall_health_score || 0) < 60).length
        };
        return distribution;
    }
    
    /**
     * Calculate lifecycle distribution
     */
    calculateLifecycleDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const phase = twin.lifecycle_phase || 'Unknown';
            distribution[phase] = (distribution[phase] || 0) + 1;
        });
        return distribution;
    }
    
    /**
     * Calculate integration status distribution
     */
    calculateIntegrationStatusDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const status = twin.integration_status || 'Unknown';
            distribution[status] = (distribution[status] || 0) + 1;
        });
        return distribution;
    }
    
    /**
     * Setup auto-refresh
     */
    setupAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(async () => {
            if (this.isAuthenticated) {
                await this.loadAnalyticsData();
            }
        }, 60000); // Refresh every minute
    }

    /**
     * Clear charts
     */
    clearCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Show loading state
     */
    showLoading() {
        const container = document.getElementById(this.elementIds.overviewCards);
        if (container) {
            container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading analytics...</div>';
        }
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        // Loading state will be replaced by actual data
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('Analytics Error:', message);
        // You can implement a toast notification system here
        alert(message);
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }
    
    /**
     * Calculate twin type distribution
     */
    calculateTwinTypeDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const type = twin.twin_type || 'Unknown';
            distribution[type] = (distribution[type] || 0) + 1;
        });
        return distribution;
    }
    
    /**
     * Calculate health distribution
     */
    calculateHealthDistribution(twins) {
        const distribution = {
            excellent: twins.filter(t => (t.overall_health_score || 0) >= 90).length,
            good: twins.filter(t => (t.overall_health_score || 0) >= 75 && (t.overall_health_score || 0) < 90).length,
            warning: twins.filter(t => (t.overall_health_score || 0) >= 60 && (t.overall_health_score || 0) < 75).length,
            critical: twins.filter(t => (t.overall_health_score || 0) < 60).length
        };
        return distribution;
    }
    
    /**
     * Calculate lifecycle distribution
     */
    calculateLifecycleDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const phase = twin.lifecycle_phase || 'Unknown';
            distribution[phase] = (distribution[phase] || 0) + 1;
        });
        return distribution;
    }
    
    /**
     * Calculate integration status distribution
     */
    calculateIntegrationStatusDistribution(twins) {
        const distribution = {};
        twins.forEach(twin => {
            const status = twin.integration_status || 'Unknown';
            distribution[status] = (distribution[status] || 0) + 1;
        });
        return distribution;
    }

    /**
     * Cleanup resources
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.clearCharts();
        this.isInitialized = false;
        console.log('🧹 Twin Registry Analytics Dashboard destroyed');
    }
}
