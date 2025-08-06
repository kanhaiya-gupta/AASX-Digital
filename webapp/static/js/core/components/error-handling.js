/**
 * Error Handling Component
 * Handles global error handling and error-related functionality
 */

export class ErrorHandler {
    constructor() {
        this.isInitialized = false;
        this.errorCallbacks = new Map();
    }

    /**
     * Initialize error handling
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('⚠️ Initializing Error Handler...');
        
        try {
            // Set up AJAX error handling
            this.setupAjaxErrorHandling();
            
            // Set up global error handling
            this.setupGlobalErrorHandling();
            
            // Set up unhandled promise rejection handling
            this.setupPromiseRejectionHandling();
            
            this.isInitialized = true;
            console.log('✅ Error Handler initialized');
            
        } catch (error) {
            console.error('❌ Error Handler initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup AJAX error handling
     */
    setupAjaxErrorHandling() {
        // Global AJAX error handler
        $(document).ajaxError((event, xhr, settings, error) => {
            this.handleAjaxError(event, xhr, settings, error);
        });
        
        // Global AJAX success handler
        $(document).ajaxSuccess((event, xhr, settings) => {
            this.handleAjaxSuccess(event, xhr, settings);
        });
    }

    /**
     * Setup global error handling
     */
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event);
        });
    }

    /**
     * Setup promise rejection handling
     */
    setupPromiseRejectionHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            this.handlePromiseRejection(event);
        });
    }

    /**
     * Handle AJAX error
     */
    handleAjaxError(event, xhr, settings, error) {
        const errorInfo = {
            url: settings.url,
            type: settings.type,
            status: xhr.status,
            statusText: xhr.statusText,
            error: error,
            timestamp: new Date().toISOString()
        };
        
        console.error('AJAX Error:', errorInfo);
        
        // Log error for debugging
        this.logError('AJAX Error', errorInfo);
        
        // Show user-friendly error message
        this.showUserError(errorInfo);
        
        // Call registered error callbacks
        this.callErrorCallbacks('ajax', errorInfo);
    }

    /**
     * Handle AJAX success
     */
    handleAjaxSuccess(event, xhr, settings) {
        const successInfo = {
            url: settings.url,
            type: settings.type,
            status: xhr.status,
            timestamp: new Date().toISOString()
        };
        
        console.log('AJAX Success:', successInfo);
        
        // Call registered success callbacks
        this.callErrorCallbacks('ajax_success', successInfo);
    }

    /**
     * Handle global error
     */
    handleGlobalError(event) {
        const errorInfo = {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error,
            timestamp: new Date().toISOString()
        };
        
        console.error('Global Error:', errorInfo);
        
        // Log error for debugging
        this.logError('Global Error', errorInfo);
        
        // Show user-friendly error message
        this.showUserError(errorInfo);
        
        // Call registered error callbacks
        this.callErrorCallbacks('global', errorInfo);
    }

    /**
     * Handle promise rejection
     */
    handlePromiseRejection(event) {
        const errorInfo = {
            reason: event.reason,
            promise: event.promise,
            timestamp: new Date().toISOString()
        };
        
        console.error('Unhandled Promise Rejection:', errorInfo);
        
        // Log error for debugging
        this.logError('Promise Rejection', errorInfo);
        
        // Show user-friendly error message
        this.showUserError(errorInfo);
        
        // Call registered error callbacks
        this.callErrorCallbacks('promise', errorInfo);
    }

    /**
     * Show user-friendly error message
     */
    showUserError(errorInfo) {
        let userMessage = 'An error occurred while processing your request.';
        
        // Customize message based on error type
        if (errorInfo.status) {
            switch (errorInfo.status) {
                case 400:
                    userMessage = 'Invalid request. Please check your input and try again.';
                    break;
                case 401:
                    userMessage = 'Authentication required. Please log in and try again.';
                    break;
                case 403:
                    userMessage = 'Access denied. You do not have permission to perform this action.';
                    break;
                case 404:
                    userMessage = 'The requested resource was not found.';
                    break;
                case 500:
                    userMessage = 'Server error. Please try again later.';
                    break;
                case 503:
                    userMessage = 'Service temporarily unavailable. Please try again later.';
                    break;
            }
        }
        
        // Show notification if available
        if (window.showNotification) {
            window.showNotification(userMessage, 'error');
        } else {
            alert(userMessage);
        }
    }

    /**
     * Log error for debugging
     */
    logError(type, errorInfo) {
        // Send error to logging service (if available)
        if (window.logError) {
            window.logError(type, errorInfo);
        }
        
        // Store error in localStorage for debugging
        try {
            const errorLog = JSON.parse(localStorage.getItem('errorLog') || '[]');
            errorLog.push({
                type,
                ...errorInfo,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 50 errors
            if (errorLog.length > 50) {
                errorLog.splice(0, errorLog.length - 50);
            }
            
            localStorage.setItem('errorLog', JSON.stringify(errorLog));
        } catch (e) {
            console.warn('Failed to log error to localStorage:', e);
        }
    }

    /**
     * Register error callback
     */
    registerErrorCallback(type, callback) {
        if (!this.errorCallbacks.has(type)) {
            this.errorCallbacks.set(type, []);
        }
        this.errorCallbacks.get(type).push(callback);
    }

    /**
     * Call registered error callbacks
     */
    callErrorCallbacks(type, errorInfo) {
        const callbacks = this.errorCallbacks.get(type);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(errorInfo);
                } catch (e) {
                    console.error('Error in error callback:', e);
                }
            });
        }
    }

    /**
     * Get error log
     */
    getErrorLog() {
        try {
            return JSON.parse(localStorage.getItem('errorLog') || '[]');
        } catch (e) {
            return [];
        }
    }

    /**
     * Clear error log
     */
    clearErrorLog() {
        localStorage.removeItem('errorLog');
    }

    /**
     * Cleanup error handler
     */
    destroy() {
        this.errorCallbacks.clear();
        this.isInitialized = false;
        console.log('🧹 Error Handler destroyed');
    }
} 