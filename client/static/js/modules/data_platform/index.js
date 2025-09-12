/**
 * Data Platform Main JavaScript Module
 * Coordinates all modular components and provides the main entry point
 * 
 * Features:
 * - Module coordination and initialization
 * - Global state management
 * - Event handling and routing
 * - Service orchestration
 */

// Import modular components
import './user-management/user_management.js';
import './dashboard.js';
import './organization-management/organization_management.js';
import './file-operations/file_operations.js';
import './project-management/project_management.js';
import './use-case-management/use_case_management.js';
import './analytics-insights/analytics_insights.js';
import './system-configuration/system_configuration.js';

// Global instances for modular components
let userManagementInstance = null;
let dashboardInstance = null;

class DataPlatformCoordinator {
    constructor() {
        this.modules = {
            dashboard: null,
            userManagement: null,
            organizationManagement: null,
            fileOperations: null,
            projectManagement: null,
            useCaseManagement: null,
            analyticsInsights: null,
        systemConfiguration: null
        };
        
        this.state = {
            isInitialized: false,
            activeTab: null
        };
        
        this.init();
    }

    /**
     * Initialize the coordinator
     */
    async init() {
        try {
            console.log('🚀 Initializing Data Platform Coordinator...');
            
            // Initialize dashboard module
            this.initializeDashboard();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Mark as initialized
            this.state.isInitialized = true;
            
            console.log('✅ Data Platform Coordinator initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing coordinator:', error);
            this.showErrorMessage('Failed to initialize coordinator. Please refresh the page.');
        }
    }

    /**
     * Initialize dashboard module
     */
    initializeDashboard() {
        try {
            this.modules.dashboard = new DashboardModule();
            dashboardInstance = this.modules.dashboard;
            console.log('✅ Dashboard module initialized');
        } catch (error) {
            console.error('❌ Error initializing dashboard module:', error);
        }
    }

    /**
     * Initialize user management module when tab is activated
     */
    initializeUserManagement() {
        if (!this.modules.userManagement) {
            try {
                this.modules.userManagement = new UserManagementModule();
                userManagementInstance = this.modules.userManagement;
                console.log('✅ User Management module initialized');
            } catch (error) {
                console.error('❌ Error initializing user management module:', error);
            }
        }
    }

    /**
     * Initialize organization management module when tab is activated
     */
    initializeOrganizationManagement() {
        if (!this.modules.organizationManagement) {
            try {
                this.modules.organizationManagement = new OrganizationManagementModule();
                console.log('✅ Organization Management module initialized');
            } catch (error) {
                console.error('❌ Error initializing organization management module:', error);
            }
        }
    }

                /**
             * Initialize file operations module when tab is activated
             */
            initializeFileOperations() {
                if (!this.modules.fileOperations) {
                    try {
                        this.modules.fileOperations = new FileOperationsModule();
                        console.log('✅ File Operations module initialized');
                    } catch (error) {
                        console.error('❌ Error initializing file operations module:', error);
                    }
                }
            }

            /**
             * Initialize project management module when tab is activated
             */
            initializeProjectManagement() {
                if (!this.modules.projectManagement) {
                    try {
                        this.modules.projectManagement = new ProjectManagementModule();
                        console.log('✅ Project Management module initialized');
                    } catch (error) {
                        console.error('❌ Error initializing project management module:', error);
                    }
                }
            }

                /**
     * Initialize use case management module when tab is activated
     */
    initializeUseCaseManagement() {
        if (!this.modules.useCaseManagement) {
            try {
                this.modules.useCaseManagement = new UseCaseManagementModule();
                console.log('✅ Use Case Management module initialized');
            } catch (error) {
                console.error('❌ Error initializing use case management module:', error);
            }
        }
    }

    /**
     * Initialize analytics insights module when tab is activated
     */
    initializeAnalyticsInsights() {
        if (!this.modules.analyticsInsights) {
            try {
                this.modules.analyticsInsights = new AnalyticsInsightsModule();
                console.log('✅ Analytics & Insights module initialized');
            } catch (error) {
                console.error('❌ Error initializing analytics insights module:', error);
            }
        }
    }

    /**
     * Initialize system configuration module when tab is activated
     */
    initializeSystemConfiguration() {
        if (!this.modules.systemConfiguration) {
            try {
                this.modules.systemConfiguration = new SystemConfigurationModule();
                console.log('✅ System Configuration module initialized');
            } catch (error) {
                console.error('❌ Error initializing system configuration module:', error);
            }
        }
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
        // Listen for tab changes
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link') && e.target.getAttribute('data-bs-toggle') === 'tab') {
                const targetTab = e.target.getAttribute('data-bs-target');
                this.handleTabChange(targetTab);
            }
        });

        // Also check if any tab is already active on page load
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab) {
            const targetTab = activeTab.getAttribute('data-bs-target');
            this.handleTabChange(targetTab);
        }
    }

    /**
     * Handle tab changes and initialize appropriate modules
     */
    handleTabChange(targetTab) {
        console.log(`🔄 Tab changed to: ${targetTab}`);
        
        if (targetTab === '#user-management-tab') {
            this.initializeUserManagement();
        } else if (targetTab === '#organization-management-tab') {
            this.initializeOrganizationManagement();
                        } else if (targetTab === '#file-operations-tab') {
                    this.initializeFileOperations();
                } else if (targetTab === '#project-management-tab') {
                    this.initializeProjectManagement();
                } else if (targetTab === '#use-case-management-tab') {
                    this.initializeUseCaseManagement();
                } else if (targetTab === '#analytics-insights-tab') {
                    this.initializeAnalyticsInsights();
                } else if (targetTab === '#system-configuration-tab') {
                    this.initializeSystemConfiguration();
                }
        
        this.state.activeTab = targetTab;
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        console.error('❌ Error:', message);
        // In a real implementation, you'd show a user-friendly error message
    }

    /**
     * Cleanup resources
     */
    destroy() {
        // Destroy all modules
        if (this.modules.dashboard) {
            this.modules.dashboard.destroy();
        }
        if (this.modules.userManagement) {
            this.modules.userManagement.destroy();
        }
        if (this.modules.organizationManagement) {
            this.modules.organizationManagement.destroy();
        }
                        if (this.modules.fileOperations) {
                    this.modules.fileOperations.destroy();
                }
                if (this.modules.projectManagement) {
                    this.modules.projectManagement.destroy();
                }
                if (this.modules.useCaseManagement) {
                    this.modules.useCaseManagement.destroy();
                }
                if (this.modules.analyticsInsights) {
                    this.modules.analyticsInsights.destroy();
                }
                if (this.modules.systemConfiguration) {
                    this.modules.systemConfiguration.destroy();
                }
        
        console.log('🧹 Data Platform Coordinator destroyed');
    }
}

// Global functions for HTML onclick handlers
function refreshDashboard() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.refreshDashboardData();
    }
}

function refreshActivityFeed() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.refreshActivityFeed();
    }
}

function viewAllActivity() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.viewAllActivity();
    }
}

function viewComplianceReport() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.viewComplianceReport();
    }
}

function scheduleAudit() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.scheduleAudit();
    }
}

function exportComplianceData() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.dashboard) {
        window.dataPlatformCoordinator.modules.dashboard.exportComplianceData();
    }
}

function switchToTab(tabName) {
    if (window.dataPlatformCoordinator) {
        window.dataPlatformCoordinator.handleTabChange(tabName);
    }
}

// Organization Management Global Functions
function showCreateOrgModal() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.showCreateOrgModal();
    }
}

function saveOrganization() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.saveOrganization();
    }
}

function filterOrganizations() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.filterOrganizations();
    }
}

function clearOrgSearch() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.clearOrgSearch();
    }
}

function toggleAdvancedFilters() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.toggleAdvancedFilters();
    }
}

function toggleSelectAllOrgs(checked) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.toggleSelectAllOrgs(checked);
    }
}

function toggleOrgSelection() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.toggleOrgSelection();
    }
}

function viewOrgDetails(orgId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.viewOrgDetails(orgId);
    }
}

function editOrganization(orgId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.editOrganization(orgId);
    }
}

function suspendOrganization(orgId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.suspendOrganization(orgId);
    }
}

function deleteOrganization(orgId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.deleteOrganization(orgId);
    }
}

function bulkActivateOrgs() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.bulkActivateOrgs();
    }
}

function bulkSuspendOrgs() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.bulkSuspendOrgs();
    }
}

function bulkDeleteOrgs() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.bulkDeleteOrgs();
    }
}

function exportOrganizationData() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.exportOrganizationData();
    }
}

function importOrganizations() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.importOrganizations();
    }
}

function changeOrgPage(page) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.organizationManagement) {
        window.dataPlatformCoordinator.modules.organizationManagement.changeOrgPage(page);
    }
}

// File Operations Global Functions
function showUploadModal() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.showUploadModal();
    }
}

function exportFileData() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.exportFileData();
    }
}

function showBulkUploadModal() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.showBulkUploadModal();
    }
}

function filterFiles() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.filterFiles();
    }
}

function clearFileSearch() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.clearFileSearch();
    }
}

function toggleFileSelection(fileId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.toggleFileSelection(fileId);
    }
}

function toggleSelectAllFiles(checked) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.toggleSelectAllFiles(checked);
    }
}

function viewFileDetails(fileId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.viewFileDetails(fileId);
    }
}

function downloadFile(fileId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.downloadFile(fileId);
    }
}

function editFile(fileId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.editFile(fileId);
    }
}

function deleteFile(fileId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.deleteFile(fileId);
    }
}

function removeFileFromQueue(index) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.removeFileFromQueue(index);
    }
}

function changeFilePage(page) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.changeFilePage(page);
    }
}

function bulkActivateFiles() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.bulkAction('activate');
    }
}

function bulkArchiveFiles() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.bulkAction('archive');
    }
}

function bulkDeleteFiles() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.bulkAction('delete');
    }
}

function bulkDownloadFiles() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.fileOperations) {
        window.dataPlatformCoordinator.modules.fileOperations.bulkAction('download');
    }
}

// Project Management Global Functions
function showCreateProjectModal() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.showCreateProjectModal();
    }
}

function showProjectTemplates() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.showProjectTemplates();
    }
}

function exportProjectData() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.exportProjectData();
    }
}

function filterProjects() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.filterProjects();
    }
}

function clearProjectSearch() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.clearProjectSearch();
    }
}

function toggleProjectSelection(projectId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.toggleProjectSelection(projectId);
    }
}

function viewProjectDetails(projectId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.viewProjectDetails(projectId);
    }
}

function editProject(projectId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.editProject(projectId);
    }
}

function deleteProject(projectId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.deleteProject(projectId);
    }
}

function changeProjectPage(page) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.changeProjectPage(page);
    }
}

function bulkActivateProjects() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.handleBulkAction('activate');
    }
}

function bulkArchiveProjects() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.handleBulkAction('archive');
    }
}

function bulkDeleteProjects() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.handleBulkAction('delete');
    }
}

function bulkExportProjects() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.projectManagement) {
        window.dataPlatformCoordinator.modules.projectManagement.handleBulkAction('export');
    }
}

// Use Case Management Global Functions
function showCreateUseCaseModal() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.showCreateUseCaseModal();
    }
}

function showUseCaseTemplates() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.showUseCaseTemplates();
    }
}

function exportUseCaseData() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.exportUseCaseData();
    }
}

function filterUseCases() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.filterUseCases();
    }
}

function clearUseCaseSearch() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.clearUseCaseSearch();
    }
}

function toggleUseCaseSelection(useCaseId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.toggleUseCaseSelection(useCaseId);
    }
}

function viewUseCaseDetails(useCaseId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.viewUseCaseDetails(useCaseId);
    }
}

function editUseCase(useCaseId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.editUseCase(useCaseId);
    }
}

function deleteUseCase(useCaseId) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.deleteUseCase(useCaseId);
    }
}

function changeUseCasePage(page) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.changeUseCasePage(page);
    }
}

function bulkApproveUseCases() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.handleBulkAction('approve');
    }
}

function bulkRejectUseCases() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.handleBulkAction('reject');
    }
}

function bulkArchiveUseCases() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.useCaseManagement) {
        window.dataPlatformCoordinator.modules.useCaseManagement.handleBulkAction('archive');
    }
}

// Analytics & Insights Global Functions
function exportAnalyticsReport() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.exportAnalyticsReport();
    }
}

function scheduleAnalyticsReport() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.scheduleAnalyticsReport();
    }
}

function createCustomDashboard() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.createCustomDashboard();
    }
}

function setTrendPeriod(period) {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.setTrendPeriod(period);
    }
}

function executeQuery() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.executeQuery();
    }
}

function saveQuery() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.saveQuery();
    }
}

function saveCustomDashboard() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.saveCustomDashboard();
    }
}

function saveScheduledReport() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.analyticsInsights) {
        window.dataPlatformCoordinator.modules.analyticsInsights.saveScheduledReport();
    }
}

// System Configuration Global Functions
function exportSystemConfig() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.systemConfiguration) {
        window.dataPlatformCoordinator.modules.systemConfiguration.exportSystemConfig();
    }
}

function backupSystemConfig() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.systemConfiguration) {
        window.dataPlatformCoordinator.modules.systemConfiguration.backupSystemConfig();
    }
}

function saveAllConfigurations() {
    if (window.dataPlatformCoordinator && window.dataPlatformCoordinator.modules.systemConfiguration) {
        window.dataPlatformCoordinator.modules.systemConfiguration.saveAllConfigurations();
    }
}

// Initialize coordinator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dataPlatformCoordinator = new DataPlatformCoordinator();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataPlatformCoordinator;
}
