/**
 * Shared Alert System for AASX Digital Twin Framework
 * Consistent notification system across all modules
 */

// Alert types and their configurations
const ALERT_TYPES = {
    success: {
        icon: 'fas fa-check-circle',
        class: 'alert-success',
        autoHide: true,
        duration: 5000
    },
    error: {
        icon: 'fas fa-exclamation-triangle',
        class: 'alert-danger',
        autoHide: false,
        duration: 0
    },
    warning: {
        icon: 'fas fa-exclamation-circle',
        class: 'alert-warning',
        autoHide: true,
        duration: 7000
    },
    info: {
        icon: 'fas fa-info-circle',
        class: 'alert-info',
        autoHide: true,
        duration: 5000
    }
};

// Global alert container
let alertContainer = null;

// Initialize alert system
export function initAlertSystem(containerId = 'alertContainer') {
    // Create alert container if it doesn't exist
    if (!document.getElementById(containerId)) {
        const container = document.createElement('div');
        container.id = containerId;
        container.className = 'alert-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    alertContainer = document.getElementById(containerId);
    
    // Add CSS for alert container
    if (!document.getElementById('alert-styles')) {
        const style = document.createElement('style');
        style.id = 'alert-styles';
        style.textContent = `
            .alert-container {
                max-width: 400px;
                z-index: 9999;
            }
            .alert-item {
                margin-bottom: 10px;
                animation: slideInRight 0.3s ease-out;
            }
            .alert-item.fade-out {
                animation: slideOutRight 0.3s ease-in;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Show alert message
export function showAlert(message, type = 'info', options = {}) {
    if (!alertContainer) {
        initAlertSystem();
    }
    
    const config = { ...ALERT_TYPES[type], ...options };
    const alertId = `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const alertHtml = `
        <div id="${alertId}" class="alert ${config.class} alert-dismissible fade show alert-item" role="alert">
            <div class="d-flex align-items-center">
                <i class="${config.icon} me-2"></i>
                <span class="flex-grow-1">${message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    const alertElement = document.getElementById(alertId);
    
    // Auto-hide if configured
    if (config.autoHide && config.duration > 0) {
        setTimeout(() => {
            hideAlert(alertId);
        }, config.duration);
    }
    
    // Add click to dismiss functionality
    alertElement.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-close')) {
            hideAlert(alertId);
        }
    });
    
    return alertId;
}

// Hide specific alert
export function hideAlert(alertId) {
    const alertElement = document.getElementById(alertId);
    if (alertElement) {
        alertElement.classList.add('fade-out');
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.parentNode.removeChild(alertElement);
            }
        }, 300);
    }
}

// Hide all alerts
export function hideAllAlerts() {
    if (alertContainer) {
        const alerts = alertContainer.querySelectorAll('.alert-item');
        alerts.forEach(alert => {
            alert.classList.add('fade-out');
        });
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 300);
    }
}

// Success alert shorthand
export function showSuccess(message, options = {}) {
    return showAlert(message, 'success', options);
}

// Error alert shorthand
export function showError(message, options = {}) {
    return showAlert(message, 'error', options);
}

// Warning alert shorthand
export function showWarning(message, options = {}) {
    return showAlert(message, 'warning', options);
}

// Info alert shorthand
export function showInfo(message, options = {}) {
    return showAlert(message, 'info', options);
}

// Confirm dialog
export function showConfirm(message, onConfirm, onCancel = null) {
    const confirmId = `confirm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const confirmHtml = `
        <div id="${confirmId}" class="modal fade" tabindex="-1" role="dialog">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Action</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary confirm-btn">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', confirmHtml);
    
    const modal = document.getElementById(confirmId);
    const confirmBtn = modal.querySelector('.confirm-btn');
    
    // Handle confirm button click
    confirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        hideModal(confirmId);
    });
    
    // Handle modal close
    modal.addEventListener('hidden.bs.modal', () => {
        if (onCancel) onCancel();
        hideModal(confirmId);
    });
    
    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    return confirmId;
}

// Hide modal
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
}

// Toast notification system
export function showToast(message, type = 'info', duration = 3000) {
    const toastId = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${ALERT_TYPES[type].icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        if (toastElement.parentNode) {
            toastElement.parentNode.removeChild(toastElement);
        }
    });
    
    return toastId;
}

// Export all alert functions
export default {
    initAlertSystem,
    showAlert,
    hideAlert,
    hideAllAlerts,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showConfirm,
    showToast
};