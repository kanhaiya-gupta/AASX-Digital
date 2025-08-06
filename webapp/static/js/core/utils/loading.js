/**
 * Loading Manager
 * Handles loading states and loading-related functionality
 */

export class LoadingManager {
    constructor() {
        this.isInitialized = false;
        this.loadingStates = new Map();
    }

    /**
     * Initialize loading manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('⏳ Initializing Loading Manager...');
        
        try {
            this.isInitialized = true;
            console.log('✅ Loading Manager initialized');
            
        } catch (error) {
            console.error('❌ Loading Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Show loading state
     */
    show(element, message = 'Loading...') {
        if (!this.isInitialized) {
            console.warn('Loading Manager not initialized');
            return;
        }

        const elementObj = typeof element === 'string' ? document.getElementById(element) : element;
        if (!elementObj) return;

        // Store original state
        const originalState = {
            content: elementObj.innerHTML,
            disabled: elementObj.disabled,
            className: elementObj.className
        };

        this.loadingStates.set(elementObj, originalState);

        // Show loading state
        elementObj.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${message}
        `;
        elementObj.disabled = true;
        elementObj.classList.add('loading');

        return elementObj;
    }

    /**
     * Hide loading state
     */
    hide(element) {
        if (!this.isInitialized) {
            console.warn('Loading Manager not initialized');
            return;
        }

        const elementObj = typeof element === 'string' ? document.getElementById(element) : element;
        if (!elementObj) return;

        const originalState = this.loadingStates.get(elementObj);
        if (!originalState) return;

        // Restore original state
        elementObj.innerHTML = originalState.content;
        elementObj.disabled = originalState.disabled;
        elementObj.className = originalState.className;

        // Remove from loading states
        this.loadingStates.delete(elementObj);

        return elementObj;
    }

    /**
     * Show loading overlay
     */
    showOverlay(message = 'Loading...', container = document.body) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;

        overlay.innerHTML = `
            <div class="loading-content text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="loading-message">${message}</div>
            </div>
        `;

        container.appendChild(overlay);
        return overlay;
    }

    /**
     * Hide loading overlay
     */
    hideOverlay(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.remove();
        }
    }

    /**
     * Show loading spinner
     */
    showSpinner(container, message = 'Loading...') {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner text-center';
        spinner.innerHTML = `
            <div class="spinner-border text-primary mb-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="text-muted">${message}</div>
        `;

        container.appendChild(spinner);
        return spinner;
    }

    /**
     * Hide loading spinner
     */
    hideSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.remove();
        }
    }

    /**
     * Show loading button
     */
    showButtonLoading(button, message = 'Loading...') {
        return this.show(button, message);
    }

    /**
     * Hide loading button
     */
    hideButtonLoading(button) {
        return this.hide(button);
    }

    /**
     * Show loading form
     */
    showFormLoading(form, message = 'Processing...') {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            this.showButtonLoading(submitButton, message);
        }
        
        // Disable all form inputs
        const inputs = form.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => {
            if (input !== submitButton) {
                input.disabled = true;
            }
        });
    }

    /**
     * Hide loading form
     */
    hideFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            this.hideButtonLoading(submitButton);
        }
        
        // Enable all form inputs
        const inputs = form.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => {
            input.disabled = false;
        });
    }

    /**
     * Check if element is loading
     */
    isLoading(element) {
        const elementObj = typeof element === 'string' ? document.getElementById(element) : element;
        return this.loadingStates.has(elementObj);
    }

    /**
     * Get loading state
     */
    getLoadingState(element) {
        const elementObj = typeof element === 'string' ? document.getElementById(element) : element;
        return this.loadingStates.get(elementObj);
    }

    /**
     * Clear all loading states
     */
    clearAll() {
        this.loadingStates.forEach((originalState, element) => {
            this.hide(element);
        });
    }

    /**
     * Cleanup loading manager
     */
    destroy() {
        this.clearAll();
        this.isInitialized = false;
        console.log('🧹 Loading Manager destroyed');
    }
} 