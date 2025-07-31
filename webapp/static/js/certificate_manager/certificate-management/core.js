/**
 * Certificate Manager Core Module
 * Handles core certificate operations, lifecycle management, and certificate functionality
 */

export default class CertificateManagerCore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/certificate-manager',
            maxCertificates: 1000,
            maxKeySize: 4096,
            supportedFormats: ['pem', 'der', 'p12', 'pfx', 'crt', 'cer'],
            supportedAlgorithms: ['RSA', 'ECDSA', 'Ed25519'],
            defaultExpiryDays: 365,
            autoRenewalEnabled: true,
            renewalThresholdDays: 30,
            revocationEnabled: true,
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            realtimeEnabled: true
        };

        this.certificates = new Map();
        this.privateKeys = new Map();
        this.certificateChains = new Map();
        this.certificateRequests = new Map();
        this.revocationList = new Map();
        this.cache = new Map();
        this.operations = [];
        this.isProcessing = false;
        this.realtimeConnections = new Map();
        this.statistics = {
            totalCertificates: 0,
            activeCertificates: 0,
            expiredCertificates: 0,
            revokedCertificates: 0,
            pendingRequests: 0,
            lastUpdate: null,
            storageSize: 0
        };
    }

    /**
     * Initialize the Certificate Manager Core
     */
    async init() {
        console.log('🔧 Initializing Certificate Manager Core...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize certificate storage
            await this.initializeCertificateStorage();

            // Load existing certificates
            await this.loadExistingCertificates();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start operation queue
            this.startOperationQueue();

            // Initialize realtime connections
            if (this.config.realtimeEnabled) {
                this.initializeRealtimeConnections();
            }

            // Start auto-renewal process
            if (this.config.autoRenewalEnabled) {
                this.startAutoRenewalProcess();
            }

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
            const response = await fetch(`${this.config.apiBaseUrl}/config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize certificate storage
     */
    async initializeCertificateStorage() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/initialize`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to initialize certificate storage: ${response.statusText}`);
            }
            
            console.log('Certificate storage initialized');
        } catch (error) {
            console.error('Certificate storage initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load existing certificates
     */
    async loadExistingCertificates() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates`);
            if (response.ok) {
                const data = await response.json();
                
                // Load certificates
                if (data.certificates) {
                    data.certificates.forEach(cert => {
                        this.certificates.set(cert.id, cert);
                    });
                }

                // Load private keys
                if (data.privateKeys) {
                    data.privateKeys.forEach(key => {
                        this.privateKeys.set(key.id, key);
                    });
                }

                // Load certificate chains
                if (data.certificateChains) {
                    data.certificateChains.forEach(chain => {
                        this.certificateChains.set(chain.id, chain);
                    });
                }

                // Load revocation list
                if (data.revocationList) {
                    data.revocationList.forEach(revoked => {
                        this.revocationList.set(revoked.serialNumber, revoked);
                    });
                }

                // Update statistics
                this.updateStatistics();
            }
        } catch (error) {
            console.error('Failed to load existing certificates:', error);
        }
    }

    /**
     * Initialize cache system
     */
    initializeCache() {
        // Set up cache cleanup interval
        setInterval(() => {
            this.cleanupCache();
        }, this.config.cacheExpiry);
    }

    /**
     * Start operation queue
     */
    startOperationQueue() {
        setInterval(() => {
            this.processOperationQueue();
        }, 1000);
    }

    /**
     * Initialize realtime connections
     */
    initializeRealtimeConnections() {
        // Set up WebSocket connections for real-time certificate updates
        const wsUrl = this.config.apiBaseUrl.replace('http', 'ws') + '/realtime';
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Certificate Manager realtime connection established');
                this.realtimeConnections.set('main', ws);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeData(data);
            };
            
            ws.onerror = (error) => {
                console.error('Certificate Manager realtime connection error:', error);
            };
            
            ws.onclose = () => {
                console.log('Certificate Manager realtime connection closed');
                this.realtimeConnections.delete('main');
                
                // Attempt to reconnect
                setTimeout(() => {
                    this.initializeRealtimeConnections();
                }, 5000);
            };
        } catch (error) {
            console.error('Failed to setup realtime connection:', error);
        }
    }

    /**
     * Start auto-renewal process
     */
    startAutoRenewalProcess() {
        setInterval(() => {
            this.checkAutoRenewal();
        }, 86400000); // Check daily
    }

    /**
     * Create a new certificate
     */
    async createCertificate(certificateData) {
        const certRequest = {
            ...certificateData,
            created: new Date().toISOString(),
            status: 'pending'
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(certRequest)
            });

            if (response.ok) {
                const certificate = await response.json();
                this.certificates.set(certificate.id, certificate);
                
                // Update cache
                this.cache.set(`cert:${certificate.id}`, {
                    data: certificate,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateCreated', {
                    detail: { certificate }
                }));

                return certificate;
            } else {
                throw new Error(`Failed to create certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate creation failed:', error);
            throw error;
        }
    }

    /**
     * Generate certificate signing request (CSR)
     */
    async generateCSR(csrData) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/csr`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(csrData)
            });

            if (response.ok) {
                const csr = await response.json();
                this.certificateRequests.set(csr.id, csr);
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('csrGenerated', {
                    detail: { csr }
                }));

                return csr;
            } else {
                throw new Error(`Failed to generate CSR: ${response.statusText}`);
            }
        } catch (error) {
            console.error('CSR generation failed:', error);
            throw error;
        }
    }

    /**
     * Import certificate
     */
    async importCertificate(certificateData, format = 'pem') {
        try {
            const formData = new FormData();
            formData.append('certificate', certificateData);
            formData.append('format', format);

            const response = await fetch(`${this.config.apiBaseUrl}/certificates/import`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const certificate = await response.json();
                this.certificates.set(certificate.id, certificate);
                
                // Update cache
                this.cache.set(`cert:${certificate.id}`, {
                    data: certificate,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateImported', {
                    detail: { certificate }
                }));

                return certificate;
            } else {
                throw new Error(`Failed to import certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate import failed:', error);
            throw error;
        }
    }

    /**
     * Export certificate
     */
    async exportCertificate(certificateId, format = 'pem') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}/export?format=${format}`);
            if (response.ok) {
                return await response.blob();
            } else {
                throw new Error(`Failed to export certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate export failed:', error);
            throw error;
        }
    }

    /**
     * Revoke certificate
     */
    async revokeCertificate(certificateId, reason = 'unspecified') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}/revoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });

            if (response.ok) {
                const revokedCert = await response.json();
                
                // Update certificate status
                const certificate = this.certificates.get(certificateId);
                if (certificate) {
                    certificate.status = 'revoked';
                    certificate.revocationDate = new Date().toISOString();
                    certificate.revocationReason = reason;
                    this.certificates.set(certificateId, certificate);
                }

                // Add to revocation list
                this.revocationList.set(revokedCert.serialNumber, revokedCert);
                
                // Update cache
                this.cache.set(`cert:${certificateId}`, {
                    data: certificate,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateRevoked', {
                    detail: { certificate, revokedCert }
                }));

                return revokedCert;
            } else {
                throw new Error(`Failed to revoke certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate revocation failed:', error);
            throw error;
        }
    }

    /**
     * Renew certificate
     */
    async renewCertificate(certificateId, renewalData = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}/renew`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(renewalData)
            });

            if (response.ok) {
                const renewedCert = await response.json();
                
                // Update certificate
                this.certificates.set(renewedCert.id, renewedCert);
                
                // Update cache
                this.cache.set(`cert:${renewedCert.id}`, {
                    data: renewedCert,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateRenewed', {
                    detail: { certificate: renewedCert }
                }));

                return renewedCert;
            } else {
                throw new Error(`Failed to renew certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate renewal failed:', error);
            throw error;
        }
    }

    /**
     * Get certificate by ID
     */
    async getCertificate(certificateId) {
        // Check cache first
        const cacheKey = `cert:${certificateId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}`);
            if (response.ok) {
                const certificate = await response.json();
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: certificate,
                    timestamp: Date.now()
                });

                return certificate;
            } else {
                throw new Error(`Failed to get certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get certificate failed:', error);
            throw error;
        }
    }

    /**
     * Get certificate chain
     */
    async getCertificateChain(certificateId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}/chain`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get certificate chain: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get certificate chain failed:', error);
            throw error;
        }
    }

    /**
     * Check certificate validity
     */
    async checkCertificateValidity(certificateId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/certificates/${certificateId}/validate`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to check certificate validity: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate validity check failed:', error);
            throw error;
        }
    }

    /**
     * Get certificate statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        const now = new Date();
        let activeCount = 0;
        let expiredCount = 0;
        let revokedCount = 0;

        for (const cert of this.certificates.values()) {
            const expiryDate = new Date(cert.notAfter);
            
            if (cert.status === 'revoked') {
                revokedCount++;
            } else if (expiryDate < now) {
                expiredCount++;
            } else {
                activeCount++;
            }
        }

        this.statistics = {
            totalCertificates: this.certificates.size,
            activeCertificates: activeCount,
            expiredCertificates: expiredCount,
            revokedCertificates: revokedCount,
            pendingRequests: this.certificateRequests.size,
            lastUpdate: new Date().toISOString(),
            storageSize: this.calculateStorageSize()
        };
    }

    /**
     * Calculate storage size
     */
    calculateStorageSize() {
        let size = 0;
        
        // Calculate certificates size
        for (const cert of this.certificates.values()) {
            size += JSON.stringify(cert).length;
        }
        
        // Calculate private keys size
        for (const key of this.privateKeys.values()) {
            size += JSON.stringify(key).length;
        }
        
        return size;
    }

    /**
     * Process operation queue
     */
    async processOperationQueue() {
        if (this.isProcessing || this.operations.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.operations.splice(0, 10);
            
            for (const operation of batch) {
                try {
                    await this.executeOperation(operation);
                } catch (error) {
                    console.error('Operation execution failed:', error);
                    // Add back to queue for retry if retries remaining
                    if (operation.retries < 3) {
                        operation.retries++;
                        this.operations.unshift(operation);
                    }
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Execute a single operation
     */
    async executeOperation(operation) {
        switch (operation.type) {
            case 'createCertificate':
                await this.createCertificate(operation.data);
                break;
            case 'revokeCertificate':
                await this.revokeCertificate(operation.certificateId, operation.reason);
                break;
            case 'renewCertificate':
                await this.renewCertificate(operation.certificateId, operation.renewalData);
                break;
            default:
                throw new Error(`Unknown operation type: ${operation.type}`);
        }
    }

    /**
     * Add operation to queue
     */
    addToQueue(operation) {
        operation.retries = 0;
        this.operations.push(operation);
    }

    /**
     * Cleanup cache
     */
    cleanupCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Handle realtime data
     */
    handleRealtimeData(data) {
        switch (data.type) {
            case 'certificate_update':
                this.handleCertificateUpdate(data.payload);
                break;
            case 'certificate_expiry':
                this.handleCertificateExpiry(data.payload);
                break;
            case 'certificate_revocation':
                this.handleCertificateRevocation(data.payload);
                break;
            default:
                console.log('Unknown realtime data type:', data.type);
        }
    }

    /**
     * Handle certificate update
     */
    handleCertificateUpdate(payload) {
        const { certificateId, certificate } = payload;
        
        // Update certificate in memory
        this.certificates.set(certificateId, certificate);
        
        // Update cache
        this.cache.set(`cert:${certificateId}`, {
            data: certificate,
            timestamp: Date.now()
        });
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('certificateUpdated', {
            detail: { certificateId, certificate }
        }));
    }

    /**
     * Handle certificate expiry
     */
    handleCertificateExpiry(payload) {
        const { certificateId, certificate } = payload;
        
        // Update certificate status
        certificate.status = 'expired';
        this.certificates.set(certificateId, certificate);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('certificateExpired', {
            detail: { certificateId, certificate }
        }));
    }

    /**
     * Handle certificate revocation
     */
    handleCertificateRevocation(payload) {
        const { certificateId, certificate, revocationData } = payload;
        
        // Update certificate status
        certificate.status = 'revoked';
        certificate.revocationDate = new Date().toISOString();
        certificate.revocationReason = revocationData.reason;
        this.certificates.set(certificateId, certificate);
        
        // Add to revocation list
        this.revocationList.set(revocationData.serialNumber, revocationData);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('certificateRevoked', {
            detail: { certificateId, certificate, revocationData }
        }));
    }

    /**
     * Check auto-renewal
     */
    async checkAutoRenewal() {
        const now = new Date();
        const thresholdDate = new Date(now.getTime() + this.config.renewalThresholdDays * 24 * 60 * 60 * 1000);

        for (const [certId, cert] of this.certificates) {
            if (cert.status === 'active') {
                const expiryDate = new Date(cert.notAfter);
                
                if (expiryDate <= thresholdDate && expiryDate > now) {
                    // Certificate needs renewal
                    this.addToQueue({
                        type: 'renewCertificate',
                        certificateId: certId,
                        renewalData: {}
                    });
                }
            }
        }
    }

    /**
     * Refresh certificate data
     */
    async refreshData() {
        try {
            await this.loadExistingCertificates();
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('certificateDataRefreshed', {
                detail: { statistics: this.statistics }
            }));
        } catch (error) {
            console.error('Data refresh failed:', error);
            throw error;
        }
    }

    /**
     * Clear all data
     */
    async clearAllData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/clear`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.certificates.clear();
                this.privateKeys.clear();
                this.certificateChains.clear();
                this.certificateRequests.clear();
                this.revocationList.clear();
                this.cache.clear();
                this.operations = [];
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateDataCleared'));
            } else {
                throw new Error(`Failed to clear data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Clear data failed:', error);
            throw error;
        }
    }

    /**
     * Export certificate data
     */
    async exportCertificateData(format = 'json', filters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ format, filters })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to export certificate data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    /**
     * Import certificate data
     */
    async importCertificateData(data, format = 'json') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ data, format })
            });

            if (response.ok) {
                await this.loadExistingCertificates();
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateDataImported', {
                    detail: { data, format }
                }));
            } else {
                throw new Error(`Failed to import certificate data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Import failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the core module
     */
    destroy() {
        this.isInitialized = false;
        
        // Close realtime connections
        for (const [key, connection] of this.realtimeConnections) {
            if (connection && connection.readyState === WebSocket.OPEN) {
                connection.close();
            }
        }
        this.realtimeConnections.clear();
        
        this.certificates.clear();
        this.privateKeys.clear();
        this.certificateChains.clear();
        this.certificateRequests.clear();
        this.revocationList.clear();
        this.cache.clear();
        this.operations = [];
        console.log('🧹 Certificate Manager Core destroyed');
    }
} 