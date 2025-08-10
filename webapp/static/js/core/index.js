/**
 * Core Module - Unified Application Core
 * Combines main.js and api.js functionality into a single modular core
 */

// Import core components
import { AppInitializer } from './components/initialization.js';
import { NavigationManager } from './components/navigation.js';
import { AutoRefreshManager } from './components/auto-refresh.js';
import { FormValidator } from './components/form-validation.js';
import { ErrorHandler } from './components/error-handling.js';
import { APIClient } from './api/client.js';
import { UIHelper } from './ui/helper.js';
// AuthUIManager is now imported from the auth module when needed

// Import utilities
import { NotificationManager } from './utils/notifications.js';
import { LoadingManager } from './utils/loading.js';
import { DebounceManager } from './utils/debounce.js';

// Core module instance
class CoreModule {
    constructor() {
        this.isInitialized = false;
        this.components = {};
        this.utils = {};
    }

    /**
     * Initialize the core module
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Initializing Core Module...');
        
        try {
            // Initialize core components
            this.components.appInitializer = new AppInitializer();
            this.components.navigation = new NavigationManager();
            this.components.autoRefresh = new AutoRefreshManager();
            this.components.formValidator = new FormValidator();
            this.components.errorHandler = new ErrorHandler();
            // AuthUIManager will be initialized by the auth module
            this.components.authUI = null;
            
            // Initialize API client
            this.components.apiClient = new APIClient();
            
            // Initialize UI helper
            this.components.uiHelper = new UIHelper(this.components.apiClient);
            
            // Initialize utilities
            this.utils.notifications = new NotificationManager();
            this.utils.loading = new LoadingManager();
            this.utils.debounce = new DebounceManager();
            
            // Initialize all components
            await this.components.appInitializer.init();
            await this.components.navigation.init();
            await this.components.autoRefresh.init();
            await this.components.formValidator.init();
            await this.components.errorHandler.init();
            // AuthUIManager will be initialized by the auth module later
            // await this.components.authUI.init();
            
            // Setup global access
            this.setupGlobalAccess();
            
            this.isInitialized = true;
            console.log('✅ Core Module initialized');
            
            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('coreModuleReady', {
                detail: { core: this }
            }));
            
        } catch (error) {
            console.error('❌ Core Module initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup global access for backward compatibility
     */
    setupGlobalAccess() {
        // Expose core utilities globally for backward compatibility
        window.showNotification = (message, type = 'info') => {
            return this.utils.notifications.show(message, type);
        };
        
        window.showLoading = (element) => {
            return this.utils.loading.show(element);
        };
        
        window.hideLoading = (element, originalText) => {
            return this.utils.loading.hide(element, originalText);
        };
        
        window.debounce = (func, wait) => {
            return this.utils.debounce.create(func, wait);
        };
        
        // Expose API client globally
        
        // Expose authentication functions globally
        window.logout = async () => {
            if (this.components.authUI) {
                await this.components.authUI.handleUserLogout();
            } else {
                console.warn('⚠️ AuthUIManager not available, logout not possible');
            }
        };
        
        window.getCurrentUser = () => {
            if (this.components.authUI) {
                return this.components.authUI.getAuthState().currentUser;
            }
            return null;
        };
        
        window.isUserAuthenticated = () => {
            if (this.components.authUI) {
                return this.components.authUI.getAuthState().isAuthenticated;
            }
            return false;
        };
        
        // Global function to update authentication UI
        window.updateAuthenticationUI = () => {
            if (this.components.authUI) {
                return this.components.authUI.checkAuthenticationAndUpdateUI();
            }
            return Promise.resolve(false);
        };
        
        // Function to set AuthUIManager from auth module
        window.setAuthUIManager = (authUI) => {
            this.components.authUI = authUI;
            console.log('✅ AuthUIManager set by auth module');
        };
        window.APIClient = APIClient;
        window.UIHelper = UIHelper;
        window.apiClient = this.components.apiClient;
        window.uiHelper = this.components.uiHelper;
        
        // Expose core module
        window.CoreModule = this;
    }

    /**
     * Get component by name
     */
    getComponent(name) {
        return this.components[name];
    }

    /**
     * Get utility by name
     */
    getUtility(name) {
        return this.utils[name];
    }

    /**
     * Cleanup core module
     */
    destroy() {
        // Cleanup all components
        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        
        // Cleanup utilities
        Object.values(this.utils).forEach(utility => {
            if (utility && typeof utility.destroy === 'function') {
                utility.destroy();
            }
        });
        
        this.isInitialized = false;
        console.log('🧹 Core Module destroyed');
    }
}

// Create and export singleton instance
const coreModule = new CoreModule();

// Initialize when DOM is ready
function initializeCore() {
    coreModule.init().catch(error => {
        console.error('Failed to initialize core module:', error);
        // Don't throw the error to prevent blocking other modules
    });
}

// Try to initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCore);
} else {
    // DOM is already ready
    initializeCore();
}

// Export for module usage
export default coreModule;

// Export individual components for direct import
export {
    AppInitializer,
    NavigationManager,
    AutoRefreshManager,
    FormValidator,
    ErrorHandler,
    APIClient,
    UIHelper,
    NotificationManager,
    LoadingManager,
    DebounceManager
}; 