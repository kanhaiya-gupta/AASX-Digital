// AASX Digital Twin Analytics Framework Main JavaScript

// Global variables
let currentModule = 'home';
let refreshInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AASX Digital Twin Analytics Framework initialized');
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Set up navigation highlighting
    highlightCurrentNav();
    
    // Set up auto-refresh for dashboard
    if (window.location.pathname === '/') {
        setupAutoRefresh();
    }
    
    // Set up form validation
    setupFormValidation();
    
    // Set up AJAX error handling
    setupAjaxErrorHandling();
});

// Highlight current navigation item
function highlightCurrentNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Setup auto-refresh for dashboard
function setupAutoRefresh() {
    // Refresh every 30 seconds
    refreshInterval = setInterval(() => {
        refreshDashboardData();
    }, 30000);
}

// Refresh dashboard data
function refreshDashboardData() {
    // This would typically make AJAX calls to update dashboard data
    console.log('Refreshing dashboard data...');
    
    // Example: Update activity feed
    updateActivityFeed();
}

// Update activity feed
function updateActivityFeed() {
    // This would fetch latest activity data
    fetch('/api/activity/latest')
        .then(response => response.json())
        .then(data => {
            // Update activity list
            console.log('Activity data updated:', data);
        })
        .catch(error => {
            console.error('Error updating activity feed:', error);
        });
}

// Setup form validation
function setupFormValidation() {
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

// Setup AJAX error handling
function setupAjaxErrorHandling() {
    // Global AJAX error handler
    $(document).ajaxError(function(event, xhr, settings, error) {
        console.error('AJAX Error:', error);
        showNotification('An error occurred while processing your request.', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at top of main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = mainContent.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Loading indicator
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading"></div> Loading...';
        element.disabled = true;
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// API helper functions
const API = {
    // GET request
    get: async function(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },
    
    // POST request
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    },
    
    // PUT request
    put: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    },
    
    // DELETE request
    delete: async function(url) {
        try {
            const response = await fetch(url, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
    }
};

// Utility functions
const Utils = {
    // Format date
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },
    
    // Format datetime
    formatDateTime: function(date) {
        return new Date(date).toLocaleString();
    },
    
    // Format number with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Generate random ID
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    }
};

// Export for use in other modules
window.QIPlatform = {
    API: API,
    Utils: Utils,
    showNotification: showNotification,
    showLoading: showLoading,
    hideLoading: hideLoading
};
