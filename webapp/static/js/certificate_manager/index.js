/**
 * Certificate Manager Module Entry Point
 * Main entry point for Certificate Management functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import Certificate Manager modules
import CertificateManagerCore from './certificate-management/core.js';
import CertificateValidator from './certificate-management/validator.js';
import CertificateStorage from './certificate-management/storage.js';
import CertificateUI from './certificate-management/ui.js';

// Global instances
let certificateManagerCore = null;
let certificateValidator = null;
let certificateStorage = null;
let certificateUI = null;

/**
 * Initialize Certificate Manager Module
 * Sets up all Certificate Manager components and functionality
 */
export async function initCertificateManagerModule() {
    console.log('🚀 Certificate Manager Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Certificate Manager
        certificateManagerCore = new CertificateManagerCore();
        await certificateManagerCore.init();
        
        // Initialize Certificate Validator
        certificateValidator = new CertificateValidator();
        await certificateValidator.init();
        
        // Initialize Certificate Storage
        certificateStorage = new CertificateStorage();
        await certificateStorage.init();
        
        // Initialize Certificate UI
        certificateUI = new CertificateUI();
        await certificateUI.init();
        
        console.log('✅ Certificate Manager Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('certificateManagerModuleReady', {
            detail: {
                certificateManagerCore,
                certificateValidator,
                certificateStorage,
                certificateUI
            }
        }));
        
    } catch (error) {
        console.error('❌ Certificate Manager module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Certificate Manager Core Instance
 */
export function getCertificateManagerCore() {
    return certificateManagerCore;
}

/**
 * Get Certificate Validator Instance
 */
export function getCertificateValidator() {
    return certificateValidator;
}

/**
 * Get Certificate Storage Instance
 */
export function getCertificateStorage() {
    return certificateStorage;
}

/**
 * Get Certificate UI Instance
 */
export function getCertificateUI() {
    return certificateUI;
}

/**
 * Cleanup Certificate Manager Module
 */
export function cleanupCertificateManagerModule() {
    if (certificateManagerCore) {
        certificateManagerCore.destroy();
        certificateManagerCore = null;
    }
    
    if (certificateValidator) {
        certificateValidator.destroy();
        certificateValidator = null;
    }
    
    if (certificateStorage) {
        certificateStorage.destroy();
        certificateStorage = null;
    }
    
    if (certificateUI) {
        certificateUI.destroy();
        certificateUI = null;
    }
    
    console.log('🧹 Certificate Manager module cleaned up');
}

/**
 * Check if Certificate Manager Module is Ready
 */
export function isCertificateManagerModuleReady() {
    return certificateManagerCore && certificateValidator && certificateStorage && certificateUI &&
           certificateManagerCore.isInitialized && certificateValidator.isInitialized && 
           certificateStorage.isInitialized && certificateUI.isInitialized;
}

/**
 * Refresh Certificate Manager Data
 */
export async function refreshCertificateManagerData() {
    if (certificateManagerCore) {
        await certificateManagerCore.refreshData();
    }
    
    if (certificateValidator) {
        await certificateValidator.refreshValidation();
    }
    
    if (certificateStorage) {
        await certificateStorage.refreshStorage();
    }
    
    if (certificateUI) {
        await certificateUI.refreshUI();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on a Certificate Manager page
    if (window.location.pathname.includes('/certificate-manager') || 
        window.location.pathname.includes('/certificates')) {
        initCertificateManagerModule().catch(error => {
            console.error('Failed to initialize Certificate Manager module:', error);
        });
    }
});

// Export for global access
window.CertificateManagerModule = {
    init: initCertificateManagerModule,
    cleanup: cleanupCertificateManagerModule,
    isReady: isCertificateManagerModuleReady,
    refresh: refreshCertificateManagerData,
    getCore: getCertificateManagerCore,
    getValidator: getCertificateValidator,
    getStorage: getCertificateStorage,
    getUI: getCertificateUI
};

// Export default
export default {
    init: initCertificateManagerModule,
    cleanup: cleanupCertificateManagerModule,
    isReady: isCertificateManagerModuleReady,
    refresh: refreshCertificateManagerData,
    getCore: getCertificateManagerCore,
    getValidator: getCertificateValidator,
    getStorage: getCertificateStorage,
    getUI: getCertificateUI
}; 