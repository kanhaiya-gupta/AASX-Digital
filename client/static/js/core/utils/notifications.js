/**
 * Notification Manager
 * Handles all notification-related functionality
 */

export class NotificationManager {
    constructor() {
        this.isInitialized = false;
        this.notificationContainer = null;
    }

    /**
     * Initialize notification manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔔 Initializing Notification Manager...');
        
        try {
            // Create notification container
            this.createNotificationContainer();
            
            this.isInitialized = true;
            console.log('✅ Notification Manager initialized');
            
        } catch (error) {
            console.error('❌ Notification Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Create notification container
     */
    createNotificationContainer() {
        this.notificationContainer = document.getElementById('notification-container');
        
        if (!this.notificationContainer) {
            this.notificationContainer = document.createElement('div');
            this.notificationContainer.id = 'notification-container';
            this.notificationContainer.className = 'notification-container position-fixed top-0 end-0 p-3';
            this.notificationContainer.style.zIndex = '9999';
            document.body.appendChild(this.notificationContainer);
        }
    }

    /**
     * Show notification
     */
    show(message, type = 'info', duration = 5000) {
        if (!this.isInitialized) {
            console.warn('Notification Manager not initialized');
            return;
        }

        const notification = document.createElement('div');
        
        // Set notification styles
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.minWidth = '300px';
        notification.style.marginBottom = '10px';
        notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        notification.style.border = 'none';
        notification.style.borderRadius = '8px';
        
        // Set icon based on type
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        else if (type === 'warning') icon = 'exclamation-triangle';
        else if (type === 'error') icon = 'times-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        return notification;
    }

    /**
     * Show success notification
     */
    showSuccess(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    /**
     * Show error notification
     */
    showError(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    /**
     * Show warning notification
     */
    showWarning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Show info notification
     */
    showInfo(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }

    /**
     * Clear all notifications
     */
    clearAll() {
        if (this.notificationContainer) {
            this.notificationContainer.innerHTML = '';
        }
    }

    /**
     * Remove specific notification
     */
    remove(notification) {
        if (notification && notification.parentNode) {
            notification.remove();
        }
    }

    /**
     * Cleanup notification manager
     */
    destroy() {
        this.clearAll();
        this.isInitialized = false;
        console.log('🧹 Notification Manager destroyed');
    }
} 