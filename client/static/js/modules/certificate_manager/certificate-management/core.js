/**
 * Certificate Manager Core Module
 * Handles core certificate management functionality
 */

export default class CertificateManagerCore {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.certificates = [];
        this.certificateChains = [];
        this.trustStores = [];
        this.revocationLists = [];
        this.isProcessing = false;
        this.processingQueue = [];
        this.errorLog = [];
        this.successLog = [];
        this.config = {
            maxCertificateSize: 10 * 1024 * 1024, // 10MB
            supportedFormats: ['pem', 'der', 'p12', 'pfx'],
            validationTimeout: 30000, // 30 seconds
            retryAttempts: 3,
            batchSize: 5
        };
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Certificate Manager Core: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Certificate Manager Core: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Certificate Manager Core: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Certificate Manager Core: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated();
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Certificate Manager Core: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Certificate Manager Core: No auth manager available');
        }
    }

    /**
     * Setup authentication event listeners
     */
    setupAuthListeners() {
        window.addEventListener('authStateChanged', () => {
            this.updateAuthState();
        });

        window.addEventListener('loginSuccess', () => {
            this.updateAuthState();
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.certificates = [];
        this.certificateChains = [];
        this.trustStores = [];
        this.revocationLists = [];
        console.log('🧹 Certificate Manager Core: Sensitive data cleared');
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Initialize the certificate manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Certificate Manager Core...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Load configuration
            await this.loadConfiguration();
            
            // Load initial data
            await this.loadCertificates();
            await this.loadCertificateChains();
            await this.loadTrustStores();
            await this.loadRevocationLists();
            
            this.isInitialized = true;
            console.log('✅ Certificate Manager Core initialized');
            
        } catch (error) {
            console.error('❌ Certificate Manager Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch('/api/certificate-manager/config', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('⚠️ Could not load certificate manager config, using defaults:', error);
        }
    }

    /**
     * Load certificates from server
     */
    async loadCertificates() {
        try {
            const response = await fetch('/api/certificate-manager/certificates', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                this.certificates = await response.json();
                console.log(`🔐 Loaded ${this.certificates.length} certificates`);
            }
        } catch (error) {
            console.error('❌ Error loading certificates:', error);
            this.certificates = [];
        }
    }

    /**
     * Load certificate chains from server
     */
    async loadCertificateChains() {
        try {
            const response = await fetch('/api/certificate-manager/certificate-chains', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                this.certificateChains = await response.json();
                console.log(`🔐 Loaded ${this.certificateChains.length} certificate chains`);
            }
        } catch (error) {
            console.error('❌ Error loading certificate chains:', error);
            this.certificateChains = [];
        }
    }

    /**
     * Load trust stores from server
     */
    async loadTrustStores() {
        try {
            const response = await fetch('/api/certificate-manager/trust-stores', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                this.trustStores = await response.json();
                console.log(`🔐 Loaded ${this.trustStores.length} trust stores`);
            }
        } catch (error) {
            console.error('❌ Error loading trust stores:', error);
            this.trustStores = [];
        }
    }

    /**
     * Load revocation lists from server
     */
    async loadRevocationLists() {
        try {
            const response = await fetch('/api/certificate-manager/revocation-lists', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                this.revocationLists = await response.json();
                console.log(`🔐 Loaded ${this.revocationLists.length} revocation lists`);
            }
        } catch (error) {
            console.error('❌ Error loading revocation lists:', error);
            this.revocationLists = [];
        }
    }

    /**
     * Add a new certificate
     */
    async addCertificate(certificateData, options = {}) {
        try {
            console.log('🔐 Adding new certificate...');
            
            const requestData = {
                certificate: certificateData,
                options: {
                    validate: options.validate !== false,
                    storeInTrustStore: options.storeInTrustStore || false,
                    metadata: options.metadata || {},
                    ...options
                }
            };
            
            const response = await fetch('/api/certificate-manager/certificates', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(requestData)
            });
            
            if (response.ok) {
                const newCertificate = await response.json();
                this.certificates.push(newCertificate);
                console.log('✅ Certificate added successfully');
                return newCertificate;
            } else {
                const error = await response.text();
                throw new Error(`Failed to add certificate: ${error}`);
            }
        } catch (error) {
            console.error('❌ Error adding certificate:', error);
            throw error;
        }
    }

    /**
     * Update an existing certificate
     */
    async updateCertificate(certificateId, updateData) {
        try {
            const response = await fetch(`/api/certificate-manager/certificates/${certificateId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(updateData)
            });
            
            if (response.ok) {
                const updatedCertificate = await response.json();
                const index = this.certificates.findIndex(c => c.id === certificateId);
                if (index !== -1) {
                    this.certificates[index] = updatedCertificate;
                }
                console.log('✅ Certificate updated successfully');
                return updatedCertificate;
            } else {
                const error = await response.text();
                throw new Error(`Failed to update certificate: ${error}`);
            }
        } catch (error) {
            console.error('❌ Error updating certificate:', error);
            throw error;
        }
    }

    /**
     * Delete a certificate
     */
    async deleteCertificate(certificateId) {
        try {
            const response = await fetch(`/api/certificate-manager/certificates/${certificateId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                this.certificates = this.certificates.filter(c => c.id !== certificateId);
                console.log('✅ Certificate deleted successfully');
                return true;
            } else {
                const error = await response.text();
                throw new Error(`Failed to delete certificate: ${error}`);
            }
        } catch (error) {
            console.error('❌ Error deleting certificate:', error);
            throw error;
        }
    }

    /**
     * Validate a certificate
     */
    async validateCertificate(certificateId) {
        try {
            console.log('🔍 Validating certificate...');
            
            const response = await fetch(`/api/certificate-manager/certificates/${certificateId}/validate`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const validationResult = await response.json();
                console.log('✅ Certificate validation completed');
                return validationResult;
            } else {
                const error = await response.text();
                throw new Error(`Certificate validation failed: ${error}`);
            }
        } catch (error) {
            console.error('❌ Error validating certificate:', error);
            throw error;
        }
    }

    /**
     * Get certificate by ID
     */
    getCertificate(certificateId) {
        return this.certificates.find(c => c.id === certificateId) || null;
    }

    /**
     * Get all certificates
     */
    getAllCertificates() {
        return [...this.certificates];
    }

    /**
     * Get certificates by status
     */
    getCertificatesByStatus(status) {
        return this.certificates.filter(c => c.status === status);
    }

    /**
     * Get certificates by organization
     */
    getCertificatesByOrganization(orgId) {
        return this.certificates.filter(c => c.organization_id === orgId);
    }

    /**
     * Search certificates
     */
    searchCertificates(query) {
        const searchTerm = query.toLowerCase();
        return this.certificates.filter(c => 
            c.subject.toLowerCase().includes(searchTerm) ||
            c.issuer.toLowerCase().includes(searchTerm) ||
            c.serialNumber.toLowerCase().includes(searchTerm)
        );
    }

    /**
     * Get processing status
     */
    getProcessingStatus() {
        return {
            isProcessing: this.isProcessing,
            queueLength: this.processingQueue.length,
            errorCount: this.errorLog.length,
            successCount: this.successLog.length
        };
    }

    /**
     * Get error log
     */
    getErrorLog() {
        return [...this.errorLog];
    }

    /**
     * Get success log
     */
    getSuccessLog() {
        return [...this.successLog];
    }

    /**
     * Clear logs
     */
    clearLogs() {
        this.errorLog = [];
        this.successLog = [];
        console.log('🧹 Logs cleared');
    }

    /**
     * Get configuration
     */
    getConfiguration() {
        return { ...this.config };
    }

    /**
     * Update configuration
     */
    updateConfiguration(newConfig) {
        this.config = { ...this.config, ...newConfig };
        console.log('⚙️ Configuration updated');
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        console.log('🔄 Refreshing certificate manager data...');
        
        try {
            await Promise.all([
                this.loadCertificates(),
                this.loadCertificateChains(),
                this.loadTrustStores(),
                this.loadRevocationLists()
            ]);
            
            console.log('✅ Certificate manager data refreshed');
        } catch (error) {
            console.error('❌ Error refreshing certificate manager data:', error);
        }
    }

    /**
     * Destroy the certificate manager
     */
    destroy() {
        this.isInitialized = false;
        this.certificates = [];
        this.certificateChains = [];
        this.trustStores = [];
        this.revocationLists = [];
        this.isProcessing = false;
        this.processingQueue = [];
        this.errorLog = [];
        this.successLog = [];
        
        console.log('🧹 Certificate Manager Core destroyed');
    }
} 