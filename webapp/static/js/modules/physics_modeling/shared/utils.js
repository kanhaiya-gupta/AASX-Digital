/**
 * Shared Utility Functions
 * Common utilities used across all physics modeling modules
 */

class PhysicsModelingUtils {
    constructor() {
        this.toastContainer = null;
        this.initToastContainer();
    }

    /**
     * Initialize toast notification container
     */
    initToastContainer() {
        if (!document.getElementById('toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            this.toastContainer.style.zIndex = '9999';
            document.body.appendChild(this.toastContainer);
        } else {
            this.toastContainer = document.getElementById('toast-container');
        }
    }

    /**
     * Show notification messages
     */
    showNotification(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        this.toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            this.toastContainer.removeChild(toast);
        });
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    /**
     * Progress indicator functions
     */
    showProgress(message = 'Processing...') {
        const progressDiv = document.getElementById('progress-indicator') || this.createProgressIndicator();
        progressDiv.querySelector('.progress-message').textContent = message;
        progressDiv.style.display = 'flex';
    }

    hideProgress() {
        const progressDiv = document.getElementById('progress-indicator');
        if (progressDiv) {
            progressDiv.style.display = 'none';
        }
    }

    createProgressIndicator() {
        const progressDiv = document.createElement('div');
        progressDiv.id = 'progress-indicator';
        progressDiv.className = 'position-fixed top-50 start-50 translate-middle bg-white border rounded p-3 shadow';
        progressDiv.style.zIndex = '9999';
        progressDiv.style.display = 'none';

        progressDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="progress-message">Processing...</span>
            </div>
        `;

        document.body.appendChild(progressDiv);
        return progressDiv;
    }

    /**
     * Form handling utilities
     */
    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            // Handle arrays and objects
            if (key.includes('[]')) {
                const arrayKey = key.replace('[]', '');
                if (!data[arrayKey]) data[arrayKey] = [];
                data[arrayKey].push(value);
            } else if (key.includes('.')) {
                // Handle nested objects
                const keys = key.split('.');
                let current = data;
                for (let i = 0; i < keys.length - 1; i++) {
                    if (!current[keys[i]]) current[keys[i]] = {};
                    current = current[keys[i]];
                }
                current[keys[keys.length - 1]] = value;
            } else {
                data[key] = value;
            }
        }

        return data;
    }

    validateForm(formId, rules = {}) {
        const form = document.getElementById(formId);
        if (!form) return { isValid: false, errors: ['Form not found'] };

        const errors = [];
        const formData = this.getFormData(formId);

        // Check required fields
        for (const [field, rule] of Object.entries(rules)) {
            if (rule.required && (!formData[field] || formData[field].toString().trim() === '')) {
                errors.push(`${field} is required`);
            }

            if (rule.minLength && formData[field] && formData[field].toString().length < rule.minLength) {
                errors.push(`${field} must be at least ${rule.minLength} characters`);
            }

            if (rule.maxLength && formData[field] && formData[field].toString().length > rule.maxLength) {
                errors.push(`${field} must be no more than ${rule.maxLength} characters`);
            }

            if (rule.pattern && formData[field] && !rule.pattern.test(formData[field])) {
                errors.push(`${field} format is invalid`);
            }

            if (rule.min && formData[field] && parseFloat(formData[field]) < rule.min) {
                errors.push(`${field} must be at least ${rule.min}`);
            }

            if (rule.max && formData[field] && parseFloat(formData[field]) > rule.max) {
                errors.push(`${field} must be no more than ${rule.max}`);
            }
        }

        return {
            isValid: errors.length === 0,
            errors: errors,
            data: formData
        };
    }

    /**
     * Data processing utilities
     */
    formatNumber(number, decimals = 2) {
        if (number === null || number === undefined) return '-';
        return parseFloat(number).toFixed(decimals);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    formatDate(date) {
        if (!date) return '-';
        return new Date(date).toLocaleString();
    }

    /**
     * Status utilities
     */
    getStatusClass(status) {
        const statusClasses = {
            'running': 'success',
            'completed': 'success',
            'failed': 'danger',
            'pending': 'warning',
            'cancelled': 'secondary',
            'validated': 'success',
            'invalid': 'danger',
            'warning': 'warning',
            'healthy': 'success',
            'unhealthy': 'danger',
            'degraded': 'warning'
        };
        return statusClasses[status.toLowerCase()] || 'secondary';
    }

    getStatusIcon(status) {
        const statusIcons = {
            'running': 'fas fa-play-circle',
            'completed': 'fas fa-check-circle',
            'failed': 'fas fa-times-circle',
            'pending': 'fas fa-clock',
            'cancelled': 'fas fa-stop-circle',
            'validated': 'fas fa-check-circle',
            'invalid': 'fas fa-times-circle',
            'warning': 'fas fa-exclamation-triangle',
            'healthy': 'fas fa-heart',
            'unhealthy': 'fas fa-heart-broken',
            'degraded': 'fas fa-heart-half'
        };
        return statusIcons[status.toLowerCase()] || 'fas fa-question-circle';
    }

    /**
     * DOM manipulation utilities
     */
    createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    }

    removeElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.remove();
        }
    }

    clearContainer(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }

    /**
     * Event handling utilities
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Local storage utilities
     */
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }

    removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    }

    /**
     * Configuration utilities
     */
    getConfig(key, defaultValue = null) {
        return this.getLocalStorage(`physics_modeling_config_${key}`, defaultValue);
    }

    setConfig(key, value) {
        this.setLocalStorage(`physics_modeling_config_${key}`, value);
    }

    /**
     * Error handling utilities
     */
    handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        
        let message = 'An error occurred';
        if (error.message) {
            message = error.message;
        } else if (typeof error === 'string') {
            message = error;
        }

        this.showError(message);
        return { success: false, error: message };
    }

    /**
     * Validation utilities
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    isValidJson(str) {
        try {
            JSON.parse(str);
            return true;
        } catch {
            return false;
        }
    }
}

// Export the utils class
export default PhysicsModelingUtils; 