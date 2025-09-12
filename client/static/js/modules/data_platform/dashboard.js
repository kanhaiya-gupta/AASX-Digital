/**
 * Dashboard Module
 * Handles all dashboard-related functionality for the Data Platform
 * 
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class DashboardModule {
    constructor() {
        this.config = {
            refreshInterval: 30000, // 30 seconds
            animationDuration: 1000,
            healthCheckInterval: 60000, // 1 minute
            maxActivityItems: 50
        };
        
        this.state = {
            isInitialized: false,
            isRefreshing: false,
            lastUpdate: null,
            userContext: null,
            systemHealth: null,
            metrics: null,
            activityFeed: [],
            complianceData: null
        };
        
        this.services = {
            userService: null,
            metricsService: null,
            healthService: null,
            activityService: null,
            complianceService: null
        };
        
        this.intervals = {
            refresh: null,
            healthCheck: null,
            activityUpdate: null
        };
        
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            console.log('🚀 Initializing Dashboard Module...');
            
            // Initialize services
            await this.initializeServices();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup real-time updates
            this.setupRealTimeUpdates();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup responsive behavior
            this.setupResponsiveBehavior();
            
            // Mark as initialized
            this.state.isInitialized = true;
            
            console.log('✅ Dashboard Module initialized successfully');
            
            // Trigger first health check
            this.performHealthCheck();
            
        } catch (error) {
            console.error('❌ Error initializing dashboard:', error);
            this.showErrorMessage('Failed to initialize dashboard. Please refresh the page.');
        }
    }

    /**
     * Initialize dashboard services
     */
    async initializeServices() {
        // In a real implementation, these would be actual service instances
        // For now, we'll create mock services for demonstration
        this.services = {
            userService: this.createMockUserService(),
            metricsService: this.createMockMetricsService(),
            healthService: this.createMockHealthService(),
            activityService: this.createMockActivityService(),
            complianceService: this.createMockComplianceService()
        };
    }

    /**
     * Load initial dashboard data
     */
    async loadInitialData() {
        try {
            // Load user context
            await this.loadUserContext();
            
            // Load real-time metrics
            await this.loadMetrics();
            
            // Load system health
            await this.loadSystemHealth();
            
            // Load activity feed
            await this.loadActivityFeed();
            
            // Load compliance data
            await this.loadComplianceData();
            
            // Update timestamp
            this.state.lastUpdate = new Date();
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            throw error;
        }
    }

    /**
     * Load user context and display information
     */
    async loadUserContext() {
        try {
            const userData = await this.services.userService.getCurrentUser();
            this.state.userContext = userData;
            
            // Update UI elements
            this.updateUserContextDisplay(userData);
            
        } catch (error) {
            console.error('❌ Error loading user context:', error);
            // Use fallback data
            this.updateUserContextDisplay({
                name: 'Administrator',
                organization: 'Enterprise Solutions Inc.',
                role: 'System Administrator'
            });
        }
    }

    /**
     * Load and display real-time metrics
     */
    async loadMetrics() {
        try {
            const metrics = await this.services.metricsService.getDashboardMetrics();
            this.state.metrics = metrics;
            
            // Update metric displays with animation
            this.updateMetricsDisplay(metrics);
            
        } catch (error) {
            console.error('❌ Error loading metrics:', error);
            // Use fallback data
            this.updateMetricsDisplay({
                users: { total: 156, active: 142, pending: 14 },
                files: { total: 1247, processed: 1189, pending: 58 },
                projects: { total: 89, onTrack: 76, atRisk: 13 },
                organizations: { total: 23, active: 21, partners: 8 }
            });
        }
    }

    /**
     * Load and display system health information
     */
    async loadSystemHealth() {
        try {
            const healthData = await this.services.healthService.getSystemHealth();
            this.state.systemHealth = healthData;
            
            // Update health display
            this.updateSystemHealthDisplay(healthData);
            
        } catch (error) {
            console.error('❌ Error loading system health:', error);
            // Use fallback data
            this.updateSystemHealthDisplay({
                overallScore: 98,
                uptime: '99.97%',
                lastCheck: '2 minutes ago',
                storage: { used: '2.4 GB', total: '10 GB', efficiency: 85, growth: 12, optimization: 92 },
                performance: { responseTime: '45ms', throughput: '1.2K req/s', errorRate: '0.01%', cacheHitRate: 94 }
            });
        }
    }

    /**
     * Load and display activity feed
     */
    async loadActivityFeed() {
        try {
            const activities = await this.services.activityService.getRecentActivities();
            this.state.activityFeed = activities;
            
            // Update activity feed display
            this.updateActivityFeedDisplay(activities);
            
        } catch (error) {
            console.error('❌ Error loading activity feed:', error);
            // Use fallback data
            this.updateActivityFeedDisplay(this.getFallbackActivityData());
        }
    }

    /**
     * Load and display compliance data
     */
    async loadComplianceData() {
        try {
            const complianceData = await this.services.complianceService.getComplianceStatus();
            this.state.complianceData = complianceData;
            
            // Update compliance display
            this.updateComplianceDisplay(complianceData);
            
        } catch (error) {
            console.error('❌ Error loading compliance data:', error);
            // Use fallback data
            this.updateComplianceDisplay({
                overall: 98,
                security: 100,
                dataGovernance: 95,
                auditTrail: 100
            });
        }
    }

    /**
     * Update user context display
     */
    updateUserContextDisplay(userData) {
        const elements = {
            userName: document.getElementById('userName'),
            orgName: document.getElementById('orgName'),
            userRole: document.getElementById('userRole')
        };
        
        if (elements.userName) elements.userName.textContent = userData.name;
        if (elements.orgName) elements.orgName.textContent = userData.organization;
        if (elements.userRole) elements.userRole.textContent = userData.role;
    }

    /**
     * Update metrics display with animations
     */
    updateMetricsDisplay(metrics) {
        // Animate metric numbers
        this.animateMetric('totalUsers', metrics.users.total);
        this.animateMetric('activeUsers', metrics.users.active);
        this.animateMetric('pendingUsers', metrics.users.pending);
        
        this.animateMetric('totalFiles', metrics.files.total);
        this.animateMetric('processedFiles', metrics.files.processed);
        this.animateMetric('pendingFiles', metrics.files.pending);
        
        this.animateMetric('totalProjects', metrics.projects.total);
        this.animateMetric('onTrackProjects', metrics.projects.onTrack);
        this.animateMetric('atRiskProjects', metrics.projects.atRisk);
        
        this.animateMetric('totalOrganizations', metrics.organizations.total);
        this.animateMetric('activeOrgs', metrics.organizations.active);
        this.animateMetric('partnerOrgs', metrics.organizations.partners);
    }

    /**
     * Update system health display
     */
    updateSystemHealthDisplay(healthData) {
        // Update health score with animation
        this.animateHealthScore(healthData.overallScore);
        
        // Update storage metrics
        const storageElements = {
            storageUsed: document.getElementById('storageUsed'),
            storageTotal: document.getElementById('storageTotal'),
            storageEfficiency: document.getElementById('storageEfficiency'),
            storageGrowth: document.getElementById('storageGrowth'),
            storageOptimization: document.getElementById('storageOptimization'),
            storageProgressBar: document.getElementById('storageProgressBar')
        };
        
        if (storageElements.storageUsed) storageElements.storageUsed.textContent = healthData.storage.used;
        if (storageElements.storageTotal) storageElements.storageTotal.textContent = healthData.storage.total;
        if (storageElements.storageEfficiency) storageElements.storageEfficiency.textContent = healthData.storage.efficiency + '%';
        if (storageElements.storageGrowth) storageElements.storageGrowth.textContent = '+' + healthData.storage.growth + '%';
        if (storageElements.storageOptimization) storageElements.storageOptimization.textContent = healthData.storage.optimization + '%';
        
        // Update storage progress bar
        if (storageElements.storageProgressBar) {
            const progressPercentage = (parseFloat(healthData.storage.used) / parseFloat(healthData.storage.total)) * 100;
            storageElements.storageProgressBar.style.width = progressPercentage + '%';
        }
        
        // Update system status
        const statusElements = {
            systemUptime: document.getElementById('systemUptime'),
            lastHealthCheck: document.getElementById('lastHealthCheck')
        };
        
        if (statusElements.systemUptime) statusElements.systemUptime.textContent = healthData.uptime;
        if (statusElements.lastHealthCheck) statusElements.lastHealthCheck.textContent = healthData.lastCheck;
    }

    /**
     * Update activity feed display
     */
    updateActivityFeedDisplay(activities) {
        const activityFeed = document.getElementById('activityFeed');
        if (!activityFeed) return;
        
        // Clear existing content
        activityFeed.innerHTML = '';
        
        // Add activity items with staggered animation
        activities.forEach((activity, index) => {
            const activityItem = this.createActivityItem(activity);
            activityItem.style.animationDelay = `${index * 0.1}s`;
            activityFeed.appendChild(activityItem);
        });
    }

    /**
     * Update compliance display
     */
    updateComplianceDisplay(complianceData) {
        const elements = {
            overallComplianceScore: document.getElementById('overallComplianceScore'),
            securityComplianceScore: document.getElementById('securityComplianceScore'),
            dataComplianceScore: document.getElementById('dataComplianceScore'),
            auditComplianceScore: document.getElementById('auditComplianceScore')
        };
        
        if (elements.overallComplianceScore) elements.overallComplianceScore.textContent = complianceData.overall + '%';
        if (elements.securityComplianceScore) elements.securityComplianceScore.textContent = complianceData.security + '%';
        if (elements.dataComplianceScore) elements.dataComplianceScore.textContent = complianceData.dataGovernance + '%';
        if (elements.auditComplianceScore) elements.auditComplianceScore.textContent = complianceData.auditTrail + '%';
    }

    /**
     * Animate metric number from 0 to target value
     */
    animateMetric(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = 0;
        const duration = this.config.animationDuration;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Use easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Animate health score
     */
    animateHealthScore(targetScore) {
        const element = document.getElementById('overallHealthScore');
        if (!element) return;
        
        const startScore = 0;
        const duration = 1500;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Use easing function
            const easeOutBack = 1 + 2.594909 * Math.pow(progress - 1, 3) + 1.594909 * Math.pow(progress - 1, 2);
            
            const currentScore = Math.floor(startScore + (targetScore - startScore) * easeOutBack);
            element.textContent = currentScore;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Create activity item element
     */
    createActivityItem(activity) {
        const item = document.createElement('div');
        item.className = 'dp-activity-item';
        item.innerHTML = `
            <div class="dp-activity-icon">
                <i class="fas ${activity.icon} ${activity.iconColor}"></i>
            </div>
            <div class="dp-activity-content">
                <div class="dp-activity-title">${activity.title}</div>
                <div class="dp-activity-desc">${activity.description}</div>
                <div class="dp-activity-meta">
                    <span class="dp-activity-time">${activity.time}</span>
                    <span class="dp-activity-user">by ${activity.user}</span>
                    <span class="dp-activity-project">${activity.project}</span>
                </div>
            </div>
            <div class="dp-activity-status">
                <span class="badge bg-${activity.statusColor}">${activity.status}</span>
            </div>
        `;
        
        return item;
    }

    /**
     * Setup real-time updates
     */
    setupRealTimeUpdates() {
        // Refresh dashboard data periodically
        this.intervals.refresh = setInterval(() => {
            this.refreshDashboardData();
        }, this.config.refreshInterval);
        
        // Perform health checks periodically
        this.intervals.healthCheck = setInterval(() => {
            this.performHealthCheck();
        }, this.config.healthCheckInterval);
        
        // Update activity feed periodically
        this.intervals.activityUpdate = setInterval(() => {
            this.updateActivityFeed();
        }, this.config.refreshInterval * 2);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('button[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshDashboardData();
            });
        }
        
        // Activity refresh button
        const activityRefreshBtn = document.querySelector('button[onclick="refreshActivityFeed()"]');
        if (activityRefreshBtn) {
            activityRefreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshActivityFeed();
            });
        }
        
        // View all activity button
        const viewAllBtn = document.querySelector('button[onclick="viewAllActivity()"]');
        if (viewAllBtn) {
            viewAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.viewAllActivity();
            });
        }
        
        // Compliance action buttons
        const complianceButtons = {
            'viewComplianceReport': () => this.viewComplianceReport(),
            'scheduleAudit': () => this.scheduleAudit(),
            'exportComplianceData': () => this.exportComplianceData()
        };
        
        Object.entries(complianceButtons).forEach(([functionName, handler]) => {
            const button = document.querySelector(`button[onclick="${functionName}()"]`);
            if (button) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    handler();
                });
            }
        });
        
        // Tab switching buttons
        const tabButtons = document.querySelectorAll('button[onclick^="switchToTab"]');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = button.getAttribute('onclick').match(/switchToTab\('([^']+)'\)/)?.[1];
                if (tabName) {
                    this.switchToTab(tabName);
                }
            });
        });
    }

    /**
     * Setup responsive behavior
     */
    setupResponsiveBehavior() {
        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
        
        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleResize();
            }, 100);
        });
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Adjust layout for different screen sizes
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth <= 1200 && window.innerWidth > 768;
        
        // Update metric grid layout
        const metricGrid = document.querySelector('.dp-metric-grid');
        if (metricGrid) {
            if (isMobile) {
                metricGrid.style.gridTemplateColumns = '1fr';
            } else if (isTablet) {
                metricGrid.style.gridTemplateColumns = 'repeat(2, 1fr)';
            } else {
                metricGrid.style.gridTemplateColumns = 'repeat(2, 1fr)';
            }
        }
        
        // Update activity feed height
        const activityFeed = document.getElementById('activityFeed');
        if (activityFeed) {
            if (isMobile) {
                activityFeed.style.maxHeight = '300px';
            } else {
                activityFeed.style.maxHeight = '400px';
            }
        }
    }

    /**
     * Refresh dashboard data
     */
    async refreshDashboardData() {
        if (this.state.isRefreshing) return;
        
        try {
            this.state.isRefreshing = true;
            this.showLoadingState();
            
            console.log('🔄 Refreshing dashboard data...');
            
            // Refresh all data
            await Promise.all([
                this.loadMetrics(),
                this.loadSystemHealth(),
                this.loadActivityFeed(),
                this.loadComplianceData()
            ]);
            
            // Update timestamp
            this.state.lastUpdate = new Date();
            
            console.log('✅ Dashboard data refreshed successfully');
            
            // Show success notification
            this.showSuccessNotification('Dashboard data refreshed successfully');
            
        } catch (error) {
            console.error('❌ Error refreshing dashboard data:', error);
            this.showErrorMessage('Failed to refresh dashboard data. Please try again.');
        } finally {
            this.state.isRefreshing = false;
            this.hideLoadingState();
        }
    }

    /**
     * Refresh activity feed
     */
    async refreshActivityFeed() {
        try {
            await this.loadActivityFeed();
            this.showSuccessNotification('Activity feed refreshed');
        } catch (error) {
            console.error('❌ Error refreshing activity feed:', error);
            this.showErrorMessage('Failed to refresh activity feed');
        }
    }

    /**
     * Perform system health check
     */
    async performHealthCheck() {
        try {
            const healthStatus = await this.services.healthService.checkHealth();
            
            // Update system status banner
            this.updateSystemStatus(healthStatus);
            
            // Log health status
            console.log('🏥 System health check completed:', healthStatus);
            
        } catch (error) {
            console.error('❌ Error performing health check:', error);
            this.updateSystemStatus({ status: 'warning', message: 'Health check failed' });
        }
    }

    /**
     * Update system status banner
     */
    updateSystemStatus(healthStatus) {
        const banner = document.getElementById('systemStatusBanner');
        if (!banner) return;
        
        const statusIndicator = banner.querySelector('.dp-status-indicator');
        const statusText = banner.querySelector('.dp-status-text');
        
        if (statusIndicator && statusText) {
            // Update status indicator
            const icon = statusIndicator.querySelector('i');
            if (icon) {
                icon.className = `fas fa-circle text-${healthStatus.status === 'healthy' ? 'success' : healthStatus.status === 'warning' ? 'warning' : 'danger'}`;
            }
            
            // Update status text
            statusText.textContent = healthStatus.message || 'System Status Unknown';
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const dashboard = document.querySelector('.dp-overview-dashboard');
        if (dashboard) {
            dashboard.classList.add('dp-loading');
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const dashboard = document.querySelector('.dp-overview-dashboard');
        if (dashboard) {
            dashboard.classList.remove('dp-loading');
        }
    }

    /**
     * Show success notification
     */
    showSuccessNotification(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        this.showNotification(message, 'danger');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Switch to specific tab
     */
    switchToTab(tabName) {
        console.log(`🔄 Switching to tab: ${tabName}`);
        // This would integrate with your tab system
        // For now, just log the action
    }

    /**
     * View all activity
     */
    viewAllActivity() {
        console.log('📋 Viewing all activity...');
        // This would navigate to a full activity log page
    }

    /**
     * View compliance report
     */
    viewComplianceReport() {
        console.log('📊 Viewing compliance report...');
        // This would open a compliance report modal or navigate to compliance tab
    }

    /**
     * Schedule audit
     */
    scheduleAudit() {
        console.log('📅 Scheduling audit...');
        // This would open an audit scheduling modal
    }

    /**
     * Export compliance data
     */
    exportComplianceData() {
        console.log('📤 Exporting compliance data...');
        // This would trigger a compliance data export
    }

    /**
     * Update activity feed
     */
    updateActivityFeed() {
        // This would check for new activities and update the feed
        console.log('📊 Checking for new activities...');
    }

    /**
     * Utility function: debounce
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Get fallback activity data
     */
    getFallbackActivityData() {
        return [
            {
                icon: 'fa-file-upload',
                iconColor: 'text-success',
                title: 'File uploaded successfully',
                description: 'thermal_analysis_v2.csv (2.4 MB)',
                time: '2 minutes ago',
                user: 'Dr. Sarah Chen',
                project: 'Project: Thermal Optimization Study',
                status: 'Completed',
                statusColor: 'success'
            },
            {
                icon: 'fa-user-plus',
                iconColor: 'text-info',
                title: 'New user account created',
                description: 'Dr. Michael Rodriguez (Research Team)',
                time: '1 hour ago',
                user: 'System Admin',
                project: 'Organization: Enterprise Solutions Inc.',
                status: 'Pending Approval',
                statusColor: 'info'
            },
            {
                icon: 'fa-project-diagram',
                iconColor: 'text-warning',
                title: 'Project status updated',
                description: 'Structural Analysis 2024 - Phase 2 completed',
                time: '3 hours ago',
                user: 'Project Manager',
                project: 'Progress: 75% → 85%',
                status: 'In Progress',
                statusColor: 'warning'
            },
            {
                icon: 'fa-chart-line',
                iconColor: 'text-primary',
                title: 'Analytics report generated',
                description: 'Monthly Performance Dashboard (Q1 2024)',
                time: '6 hours ago',
                user: 'Analytics Engine',
                project: 'Report: Executive Summary',
                status: 'Generated',
                statusColor: 'primary'
            },
            {
                icon: 'fa-shield-alt',
                iconColor: 'text-success',
                title: 'Security scan completed',
                description: 'Vulnerability assessment - No threats detected',
                time: '12 hours ago',
                user: 'Security System',
                project: 'Scan: Full System',
                status: 'Secure',
                statusColor: 'success'
            }
        ];
    }

    /**
     * Create mock services for demonstration
     */
    createMockUserService() {
        return {
            async getCurrentUser() {
                return {
                    name: 'Administrator',
                    organization: 'Enterprise Solutions Inc.',
                    role: 'System Administrator'
                };
            }
        };
    }

    createMockMetricsService() {
        return {
            async getDashboardMetrics() {
                return {
                    users: { total: 156, active: 142, pending: 14 },
                    files: { total: 1247, processed: 1189, pending: 58 },
                    projects: { total: 89, onTrack: 76, atRisk: 13 },
                    organizations: { total: 23, active: 21, partners: 8 }
                };
            }
        };
    }

    createMockHealthService() {
        return {
            async getSystemHealth() {
                return {
                    overallScore: 98,
                    uptime: '99.97%',
                    lastCheck: '2 minutes ago',
                    storage: { used: '2.4 GB', total: '10 GB', efficiency: 85, growth: 12, optimization: 92 },
                    performance: { responseTime: '45ms', throughput: '1.2K req/s', errorRate: '0.01%', cacheHitRate: 94 }
                };
            },
            async checkHealth() {
                return { status: 'healthy', message: 'All Systems Operational' };
            }
        };
    }

    createMockActivityService() {
        return {
            async getRecentActivities() {
                return this.getFallbackActivityData();
            }
        };
    }

    createMockComplianceService() {
        return {
            async getComplianceStatus() {
                return {
                    overall: 98,
                    security: 100,
                    dataGovernance: 95,
                    auditTrail: 100
                };
            }
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        // Clear intervals
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        
        // Remove event listeners
        // (In a real implementation, you'd want to properly remove all event listeners)
        
        console.log('🧹 Dashboard Module destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardModule;
} else if (typeof window !== 'undefined') {
    window.DashboardModule = DashboardModule;
}
