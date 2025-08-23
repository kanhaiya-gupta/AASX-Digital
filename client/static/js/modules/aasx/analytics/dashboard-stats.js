/**
 * Dashboard Stats Updater for AASX-ETL Frontend
 * 
 * This module integrates the main dashboard with real-time analytics data
 * from our backend APIs, replacing static placeholder values.
 * 
 * Phase 5.2: Frontend Data Integration
 */

class DashboardStats {
    constructor() {
        this.analyticsService = null;
        this.isInitialized = false;
        this.updateInterval = null;
        this.updateFrequency = 30000; // 30 seconds
    }

    /**
     * Initialize the dashboard integration
     */
    async init() {
        if (this.isInitialized) {
            console.log('⚠️ Dashboard Integration already initialized, skipping...');
            return;
        }

        console.log('🔄 Dashboard Integration initializing...');

        try {
            // Wait for analytics API to be available
            await this.waitForAnalyticsAPI();
            
            // Initialize analytics service
            this.analyticsService = new window.AnalyticsAPI();
            await this.analyticsService.init();
            
            // Load initial dashboard data
            await this.loadDashboardData();
            
            // Set up auto-refresh
            this.setupAutoRefresh();
            
            // Set up manual refresh button
            this.setupRefreshButton();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Integration initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Dashboard Integration:', error);
            this.isInitialized = false;
        }
    }

    /**
     * Wait for analytics API to be available
     */
    async waitForAnalyticsAPI() {
        console.log('⏳ Dashboard Stats: Waiting for AnalyticsAPI...');
        
        while (!window.AnalyticsAPI) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Dashboard Stats: AnalyticsAPI available');
    }

    /**
     * Load and display dashboard data
     */
    async loadDashboardData() {
        try {
            console.log('📊 Loading dashboard data...');
            
            // Show loading state
            this.showLoadingState();
            
            // Get dashboard overview and summary cards
            const [dashboardOverview, summaryCards] = await Promise.all([
                this.analyticsService.getDashboardOverview(),
                this.analyticsService.getDashboardSummaryCards()
            ]);
            
            // Update dashboard stats
            this.updateDashboardStats(dashboardOverview, summaryCards);
            
            // Hide loading state
            this.hideLoadingState();
            
            console.log('✅ Dashboard data loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load dashboard data:', error);
            this.hideLoadingState();
            this.showErrorState('Failed to load dashboard data');
        }
    }

    /**
     * Update dashboard statistics with real data
     */
    updateDashboardStats(dashboardOverview, summaryCards) {
        try {
            // Update main dashboard stats
            if (dashboardOverview.success && dashboardOverview.data) {
                this.updateMainDashboardStats(dashboardOverview.data);
            }
            
            // Update summary cards
            if (summaryCards.success && summaryCards.data) {
                this.updateSummaryCards(summaryCards.data);
            }
            
            // Update trend indicators
            this.updateTrendIndicators(dashboardOverview, summaryCards);
            
        } catch (error) {
            console.error('❌ Error updating dashboard stats:', error);
        }
    }

    /**
     * Update main dashboard statistics
     */
    updateMainDashboardStats(data) {
        // Update Total Projects
        const totalProjectsElement = document.getElementById('dashboardTotalProjects');
        if (totalProjectsElement && data.summary_cards) {
            const projectsCard = data.summary_cards.find(card => 
                card.title.toLowerCase().includes('project'));
            if (projectsCard) {
                totalProjectsElement.textContent = projectsCard.value || 0;
            }
        }

        // Update Total Files
        const totalFilesElement = document.getElementById('dashboardTotalFiles');
        if (totalFilesElement && data.summary_cards) {
            const filesCard = data.summary_cards.find(card => 
                card.title.toLowerCase().includes('file') && 
                !card.title.toLowerCase().includes('processed'));
            if (filesCard) {
                totalFilesElement.textContent = filesCard.value || 0;
            }
        }

        // Update Processed Files
        const processedFilesElement = document.getElementById('dashboardProcessedFiles');
        if (processedFilesElement && data.summary_cards) {
            const processedCard = data.summary_cards.find(card => 
                card.title.toLowerCase().includes('processed'));
            if (processedCard) {
                processedFilesElement.textContent = processedCard.value || 0;
            }
        }

        // Update Success Rate
        const successRateElement = document.getElementById('dashboardSuccessRate');
        if (successRateElement && data.summary_cards) {
            const successCard = data.summary_cards.find(card => 
                card.title.toLowerCase().includes('success'));
            if (successCard) {
                successRateElement.textContent = successCard.value || '0%';
            }
        }
    }

    /**
     * Update summary cards with real data
     */
    updateSummaryCards(summaryCards) {
        summaryCards.forEach((card, index) => {
            const cardElement = document.querySelector(`.aasx-dashboard-stat:nth-child(${index + 1})`);
            if (cardElement) {
                // Update value
                const valueElement = cardElement.querySelector('.aasx-dashboard-stat-number');
                if (valueElement) {
                    valueElement.textContent = card.value || 0;
                }

                // Update trend
                const trendElement = cardElement.querySelector('.aasx-dashboard-stat-trend');
                if (trendElement && card.trend !== undefined) {
                    this.updateTrendIndicator(trendElement, card.trend);
                }
            }
        });
    }

    /**
     * Update trend indicators
     */
    updateTrendIndicators(dashboardOverview, summaryCards) {
        // Update trend arrows and colors based on data
        const trendElements = document.querySelectorAll('.aasx-dashboard-stat-trend');
        
        trendElements.forEach((trendElement, index) => {
            if (summaryCards.success && summaryCards.data[index]) {
                const card = summaryCards.data[index];
                this.updateTrendIndicator(trendElement, card.trend || 0);
            }
        });
    }

    /**
     * Update individual trend indicator
     */
    updateTrendIndicator(trendElement, trendValue) {
        const arrowElement = trendElement.querySelector('i');
        const textElement = trendElement.querySelector('span');
        
        if (arrowElement && textElement) {
            // Update arrow direction
            if (trendValue > 0) {
                arrowElement.className = 'fas fa-arrow-up';
                trendElement.className = 'aasx-dashboard-stat-trend aasx-trend-up';
            } else if (trendValue < 0) {
                arrowElement.className = 'fas fa-arrow-down';
                trendElement.className = 'aasx-dashboard-stat-trend aasx-trend-down';
            } else {
                arrowElement.className = 'fas fa-minus';
                trendElement.className = 'aasx-dashboard-stat-trend aasx-trend-neutral';
            }
            
            // Update trend text
            const absValue = Math.abs(trendValue);
            if (trendValue > 0) {
                textElement.textContent = `+${absValue}% this period`;
            } else if (trendValue < 0) {
                textElement.textContent = `${absValue}% this period`;
            } else {
                textElement.textContent = 'No change';
            }
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const dashboardStats = document.querySelectorAll('.aasx-dashboard-stat-number');
        dashboardStats.forEach(stat => {
            stat.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        });
        
        // Add loading class to dashboard
        const dashboardSection = document.querySelector('.aasx-dashboard-stats');
        if (dashboardSection) {
            dashboardSection.classList.add('loading');
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        // Remove loading class from dashboard
        const dashboardSection = document.querySelector('.aasx-dashboard-stats');
        if (dashboardSection) {
            dashboardSection.classList.remove('loading');
        }
    }

    /**
     * Show error state
     */
    showErrorState(message) {
        console.error('❌ Dashboard Error:', message);
        
        // Show error in dashboard stats
        const dashboardStats = document.querySelectorAll('.aasx-dashboard-stat-number');
        dashboardStats.forEach(stat => {
            stat.innerHTML = '<i class="fas fa-exclamation-triangle text-warning"></i>';
            stat.title = message;
        });
    }

    /**
     * Set up auto-refresh functionality
     */
    setupAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(async () => {
            if (this.isInitialized) {
                console.log('🔄 Auto-refreshing dashboard data...');
                await this.loadDashboardData();
            }
        }, this.updateFrequency);
        
        console.log(`🔄 Auto-refresh set to ${this.updateFrequency / 1000} seconds`);
    }

    /**
     * Set up manual refresh button
     */
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                console.log('🔄 Manual refresh triggered');
                
                // Show loading state
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Refreshing...</span>';
                refreshBtn.disabled = true;
                
                try {
                    await this.loadDashboardData();
                    console.log('✅ Manual refresh completed');
                } catch (error) {
                    console.error('❌ Manual refresh failed:', error);
                } finally {
                    // Restore button state
                    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> <span>Refresh</span>';
                    refreshBtn.disabled = false;
                }
            });
        }
    }

    /**
     * Refresh dashboard data manually
     */
    async refreshDashboard() {
        if (this.isInitialized) {
            await this.loadDashboardData();
        }
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('🛑 Auto-refresh stopped');
        }
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.stopAutoRefresh();
        this.isInitialized = false;
        console.log('🗑️ Dashboard Integration destroyed');
    }
}

// Export for use in other modules
window.DashboardStats = DashboardStats;
