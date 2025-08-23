/**
 * App Initialization Component
 * Handles application startup, tooltips, popovers, and global setup
 */

export class AppInitializer {
    constructor() {
        this.isInitialized = false;
        this.tooltipList = [];
        this.popoverList = [];
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Initializing Application...');
        
        try {
            // Initialize Bootstrap components
            this.initializeTooltips();
            this.initializePopovers();
            
            // Set up navigation highlighting
            this.highlightCurrentNav();
            
            // Set up auto-refresh for dashboard
            if (window.location.pathname === '/') {
                this.setupAutoRefresh();
            }
            
            // Set up form validation
            this.setupFormValidation();
            
            // Set up AJAX error handling
            this.setupAjaxErrorHandling();
            
            this.isInitialized = true;
            console.log('✅ Application initialized');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        this.tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Initialize Bootstrap popovers
     */
    initializePopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        this.popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    /**
     * Highlight current navigation item
     */
    highlightCurrentNav() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Setup auto-refresh for dashboard
     */
    setupAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshDashboardData();
        }, 30000);
    }

    /**
     * Refresh dashboard data
     */
    refreshDashboardData() {
        console.log('Refreshing dashboard data...');
        
        // Example: Update activity feed
        this.updateActivityFeed();
    }

    /**
     * Update activity feed
     */
    updateActivityFeed() {
        fetch('/api/activity/latest')
            .then(response => response.json())
            .then(data => {
                console.log('Activity data updated:', data);
            })
            .catch(error => {
                console.error('Error updating activity feed:', error);
            });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    /**
     * Setup AJAX error handling
     */
    setupAjaxErrorHandling() {
        // Global AJAX error handler
        $(document).ajaxError(function(event, xhr, settings, error) {
            console.error('AJAX Error:', {
                url: settings.url,
                type: settings.type,
                status: xhr.status,
                error: error
            });
            
            // Show error notification
            if (window.showNotification) {
                window.showNotification('An error occurred while processing your request.', 'error');
            }
        });
    }

    /**
     * Cleanup initialization
     */
    destroy() {
        // Clear refresh interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destroy tooltips
        this.tooltipList.forEach(tooltip => {
            if (tooltip && typeof tooltip.destroy === 'function') {
                tooltip.destroy();
            }
        });
        
        // Destroy popovers
        this.popoverList.forEach(popover => {
            if (popover && typeof popover.destroy === 'function') {
                popover.destroy();
            }
        });
        
        this.isInitialized = false;
        console.log('🧹 App Initializer destroyed');
    }
} 