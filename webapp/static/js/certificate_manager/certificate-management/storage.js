/**
 * Certificate Storage Module
 * Handles certificate storage, retrieval, and management operations
 */

export default class CertificateStorage {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/certificate-manager',
            storageEnabled: true,
            encryptionEnabled: true,
            compressionEnabled: true,
            backupEnabled: true,
            backupInterval: 3600000, // 1 hour
            maxStorageSize: 100 * 1024 * 1024, // 100MB
            maxCertificates: 10000,
            supportedFormats: ['pem', 'der', 'p12', 'pfx', 'crt', 'cer'],
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            autoCleanup: true,
            cleanupInterval: 86400000 // 24 hours
        };

        this.storage = new Map();
        this.metadata = new Map();
        this.indexes = new Map();
        this.cache = new Map();
        this.backupQueue = [];
        this.cleanupQueue = [];
        this.isProcessing = false;
        this.statistics = {
            totalCertificates: 0,
            totalSize: 0,
            availableSpace: 0,
            lastBackup: null,
            lastCleanup: null,
            cacheHits: 0,
            cacheMisses: 0,
            storageErrors: 0
        };
    }

    /**
     * Initialize the Certificate Storage
     */
    async init() {
        console.log('🔧 Initializing Certificate Storage...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize storage system
            await this.initializeStorageSystem();

            // Load existing certificates
            await this.loadExistingCertificates();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Initialize indexes
            this.initializeIndexes();

            // Start backup process
            if (this.config.backupEnabled) {
                this.startBackupProcess();
            }

            // Start cleanup process
            if (this.config.autoCleanup) {
                this.startCleanupProcess();
            }

            this.isInitialized = true;
            console.log('✅ Certificate Storage initialized');

        } catch (error) {
            console.error('❌ Certificate Storage initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load storage configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize storage system
     */
    async initializeStorageSystem() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/initialize`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to initialize storage system: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.statistics.availableSpace = data.availableSpace || this.config.maxStorageSize;
            
            console.log('Storage system initialized');
        } catch (error) {
            console.error('Storage system initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load existing certificates
     */
    async loadExistingCertificates() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates`);
            if (response.ok) {
                const data = await response.json();
                
                // Load certificates
                if (data.certificates) {
                    data.certificates.forEach(cert => {
                        this.storage.set(cert.id, cert);
                        this.updateIndexes(cert);
                    });
                }

                // Load metadata
                if (data.metadata) {
                    data.metadata.forEach(meta => {
                        this.metadata.set(meta.id, meta);
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
     * Initialize indexes
     */
    initializeIndexes() {
        // Subject index
        this.indexes.set('subject', new Map());
        
        // Issuer index
        this.indexes.set('issuer', new Map());
        
        // Serial number index
        this.indexes.set('serialNumber', new Map());
        
        // Status index
        this.indexes.set('status', new Map());
        
        // Expiry date index
        this.indexes.set('expiryDate', new Map());
        
        // Type index
        this.indexes.set('type', new Map());
        
        // Tags index
        this.indexes.set('tags', new Map());
    }

    /**
     * Start backup process
     */
    startBackupProcess() {
        setInterval(() => {
            this.performBackup();
        }, this.config.backupInterval);
    }

    /**
     * Start cleanup process
     */
    startCleanupProcess() {
        setInterval(() => {
            this.performCleanup();
        }, this.config.cleanupInterval);
    }

    /**
     * Store certificate
     */
    async storeCertificate(certificate, metadata = {}) {
        try {
            // Check storage limits
            if (this.storage.size >= this.config.maxCertificates) {
                throw new Error('Maximum number of certificates reached');
            }

            const certSize = this.calculateCertificateSize(certificate);
            if (this.statistics.totalSize + certSize > this.config.maxStorageSize) {
                throw new Error('Storage space limit exceeded');
            }

            // Prepare certificate for storage
            const storedCertificate = {
                ...certificate,
                storedAt: new Date().toISOString(),
                size: certSize,
                metadata: {
                    ...metadata,
                    lastAccessed: new Date().toISOString(),
                    accessCount: 0
                }
            };

            // Store certificate
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(storedCertificate)
            });

            if (response.ok) {
                const storedCert = await response.json();
                
                // Update local storage
                this.storage.set(storedCert.id, storedCert);
                this.metadata.set(storedCert.id, storedCert.metadata);
                this.updateIndexes(storedCert);
                
                // Update cache
                this.cache.set(`cert:${storedCert.id}`, {
                    data: storedCert,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateStored', {
                    detail: { certificate: storedCert }
                }));

                return storedCert;
            } else {
                throw new Error(`Failed to store certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate storage failed:', error);
            this.statistics.storageErrors++;
            throw error;
        }
    }

    /**
     * Retrieve certificate
     */
    async retrieveCertificate(certificateId) {
        // Check cache first
        const cacheKey = `cert:${certificateId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            this.statistics.cacheHits++;
            this.updateAccessMetadata(certificateId);
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates/${certificateId}`);
            if (response.ok) {
                const certificate = await response.json();
                
                // Update local storage
                this.storage.set(certificate.id, certificate);
                this.metadata.set(certificate.id, certificate.metadata);
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: certificate,
                    timestamp: Date.now()
                });

                this.statistics.cacheMisses++;
                this.updateAccessMetadata(certificateId);
                
                return certificate;
            } else {
                throw new Error(`Failed to retrieve certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate retrieval failed:', error);
            throw error;
        }
    }

    /**
     * Update certificate
     */
    async updateCertificate(certificateId, updates) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates/${certificateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });

            if (response.ok) {
                const updatedCert = await response.json();
                
                // Update local storage
                this.storage.set(updatedCert.id, updatedCert);
                this.metadata.set(updatedCert.id, updatedCert.metadata);
                this.updateIndexes(updatedCert);
                
                // Update cache
                this.cache.set(`cert:${updatedCert.id}`, {
                    data: updatedCert,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateUpdated', {
                    detail: { certificate: updatedCert }
                }));

                return updatedCert;
            } else {
                throw new Error(`Failed to update certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate update failed:', error);
            throw error;
        }
    }

    /**
     * Delete certificate
     */
    async deleteCertificate(certificateId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates/${certificateId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Remove from local storage
                const certificate = this.storage.get(certificateId);
                this.storage.delete(certificateId);
                this.metadata.delete(certificateId);
                this.removeFromIndexes(certificate);
                
                // Remove from cache
                this.cache.delete(`cert:${certificateId}`);

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateDeleted', {
                    detail: { certificateId, certificate }
                }));

                return true;
            } else {
                throw new Error(`Failed to delete certificate: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate deletion failed:', error);
            throw error;
        }
    }

    /**
     * Search certificates
     */
    async searchCertificates(query, filters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, filters })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Search failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate search failed:', error);
            throw error;
        }
    }

    /**
     * Get certificates by filter
     */
    async getCertificatesByFilter(filter) {
        const results = [];
        
        for (const [id, certificate] of this.storage) {
            if (this.matchesFilter(certificate, filter)) {
                results.push(certificate);
            }
        }
        
        return results;
    }

    /**
     * Get certificates by status
     */
    async getCertificatesByStatus(status) {
        return this.getCertificatesByFilter({ status });
    }

    /**
     * Get certificates by issuer
     */
    async getCertificatesByIssuer(issuer) {
        return this.getCertificatesByFilter({ issuer });
    }

    /**
     * Get certificates by subject
     */
    async getCertificatesBySubject(subject) {
        return this.getCertificatesByFilter({ subject });
    }

    /**
     * Get expiring certificates
     */
    async getExpiringCertificates(days = 30) {
        const results = [];
        const threshold = new Date();
        threshold.setDate(threshold.getDate() + days);
        
        for (const [id, certificate] of this.storage) {
            const expiryDate = new Date(certificate.notAfter);
            if (expiryDate <= threshold && certificate.status === 'active') {
                results.push(certificate);
            }
        }
        
        return results;
    }

    /**
     * Get certificate metadata
     */
    async getCertificateMetadata(certificateId) {
        return this.metadata.get(certificateId) || null;
    }

    /**
     * Update certificate metadata
     */
    async updateCertificateMetadata(certificateId, metadata) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/certificates/${certificateId}/metadata`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(metadata)
            });

            if (response.ok) {
                const updatedMetadata = await response.json();
                this.metadata.set(certificateId, updatedMetadata);
                
                // Update cache
                const cached = this.cache.get(`cert:${certificateId}`);
                if (cached) {
                    cached.data.metadata = updatedMetadata;
                }
                
                return updatedMetadata;
            } else {
                throw new Error(`Failed to update metadata: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Metadata update failed:', error);
            throw error;
        }
    }

    /**
     * Add certificate tags
     */
    async addCertificateTags(certificateId, tags) {
        const metadata = this.metadata.get(certificateId) || {};
        const existingTags = metadata.tags || [];
        const newTags = [...new Set([...existingTags, ...tags])];
        
        return await this.updateCertificateMetadata(certificateId, {
            ...metadata,
            tags: newTags
        });
    }

    /**
     * Remove certificate tags
     */
    async removeCertificateTags(certificateId, tags) {
        const metadata = this.metadata.get(certificateId) || {};
        const existingTags = metadata.tags || [];
        const newTags = existingTags.filter(tag => !tags.includes(tag));
        
        return await this.updateCertificateMetadata(certificateId, {
            ...metadata,
            tags: newTags
        });
    }

    /**
     * Get certificates by tags
     */
    async getCertificatesByTags(tags) {
        const results = [];
        
        for (const [id, certificate] of this.storage) {
            const metadata = this.metadata.get(id) || {};
            const certificateTags = metadata.tags || [];
            
            if (tags.some(tag => certificateTags.includes(tag))) {
                results.push(certificate);
            }
        }
        
        return results;
    }

    /**
     * Export certificates
     */
    async exportCertificates(certificateIds, format = 'pem') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificateIds, format })
            });

            if (response.ok) {
                return await response.blob();
            } else {
                throw new Error(`Export failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate export failed:', error);
            throw error;
        }
    }

    /**
     * Import certificates
     */
    async importCertificates(certificates, metadata = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificates, metadata })
            });

            if (response.ok) {
                const importedCerts = await response.json();
                
                // Update local storage
                importedCerts.forEach(cert => {
                    this.storage.set(cert.id, cert);
                    this.metadata.set(cert.id, cert.metadata);
                    this.updateIndexes(cert);
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificatesImported', {
                    detail: { certificates: importedCerts }
                }));

                return importedCerts;
            } else {
                throw new Error(`Import failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate import failed:', error);
            throw error;
        }
    }

    /**
     * Perform backup
     */
    async performBackup() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/backup`, {
                method: 'POST'
            });

            if (response.ok) {
                const backup = await response.json();
                this.statistics.lastBackup = new Date().toISOString();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateBackupCompleted', {
                    detail: { backup }
                }));
                
                console.log('Certificate backup completed');
            } else {
                throw new Error(`Backup failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate backup failed:', error);
        }
    }

    /**
     * Perform cleanup
     */
    async performCleanup() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/storage/cleanup`, {
                method: 'POST'
            });

            if (response.ok) {
                const cleanup = await response.json();
                this.statistics.lastCleanup = new Date().toISOString();
                
                // Update local storage
                if (cleanup.removedCertificates) {
                    cleanup.removedCertificates.forEach(id => {
                        this.storage.delete(id);
                        this.metadata.delete(id);
                        this.cache.delete(`cert:${id}`);
                    });
                }

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('certificateCleanupCompleted', {
                    detail: { cleanup }
                }));
                
                console.log('Certificate cleanup completed');
            } else {
                throw new Error(`Cleanup failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Certificate cleanup failed:', error);
        }
    }

    /**
     * Get storage statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        let totalSize = 0;
        
        for (const cert of this.storage.values()) {
            totalSize += cert.size || 0;
        }
        
        this.statistics = {
            totalCertificates: this.storage.size,
            totalSize,
            availableSpace: this.config.maxStorageSize - totalSize,
            lastBackup: this.statistics.lastBackup,
            lastCleanup: this.statistics.lastCleanup,
            cacheHits: this.statistics.cacheHits,
            cacheMisses: this.statistics.cacheMisses,
            storageErrors: this.statistics.storageErrors
        };
    }

    /**
     * Update indexes
     */
    updateIndexes(certificate) {
        // Subject index
        if (certificate.subject) {
            if (!this.indexes.get('subject').has(certificate.subject)) {
                this.indexes.get('subject').set(certificate.subject, []);
            }
            this.indexes.get('subject').get(certificate.subject).push(certificate.id);
        }
        
        // Issuer index
        if (certificate.issuer) {
            if (!this.indexes.get('issuer').has(certificate.issuer)) {
                this.indexes.get('issuer').set(certificate.issuer, []);
            }
            this.indexes.get('issuer').get(certificate.issuer).push(certificate.id);
        }
        
        // Serial number index
        if (certificate.serialNumber) {
            this.indexes.get('serialNumber').set(certificate.serialNumber, certificate.id);
        }
        
        // Status index
        if (certificate.status) {
            if (!this.indexes.get('status').has(certificate.status)) {
                this.indexes.get('status').set(certificate.status, []);
            }
            this.indexes.get('status').get(certificate.status).push(certificate.id);
        }
        
        // Expiry date index
        if (certificate.notAfter) {
            const expiryKey = new Date(certificate.notAfter).toISOString().split('T')[0];
            if (!this.indexes.get('expiryDate').has(expiryKey)) {
                this.indexes.get('expiryDate').set(expiryKey, []);
            }
            this.indexes.get('expiryDate').get(expiryKey).push(certificate.id);
        }
        
        // Type index
        if (certificate.type) {
            if (!this.indexes.get('type').has(certificate.type)) {
                this.indexes.get('type').set(certificate.type, []);
            }
            this.indexes.get('type').get(certificate.type).push(certificate.id);
        }
        
        // Tags index
        const metadata = this.metadata.get(certificate.id);
        if (metadata && metadata.tags) {
            metadata.tags.forEach(tag => {
                if (!this.indexes.get('tags').has(tag)) {
                    this.indexes.get('tags').set(tag, []);
                }
                this.indexes.get('tags').get(tag).push(certificate.id);
            });
        }
    }

    /**
     * Remove from indexes
     */
    removeFromIndexes(certificate) {
        // Subject index
        if (certificate.subject) {
            const subjectIds = this.indexes.get('subject').get(certificate.subject);
            if (subjectIds) {
                const index = subjectIds.indexOf(certificate.id);
                if (index > -1) {
                    subjectIds.splice(index, 1);
                }
                if (subjectIds.length === 0) {
                    this.indexes.get('subject').delete(certificate.subject);
                }
            }
        }
        
        // Issuer index
        if (certificate.issuer) {
            const issuerIds = this.indexes.get('issuer').get(certificate.issuer);
            if (issuerIds) {
                const index = issuerIds.indexOf(certificate.id);
                if (index > -1) {
                    issuerIds.splice(index, 1);
                }
                if (issuerIds.length === 0) {
                    this.indexes.get('issuer').delete(certificate.issuer);
                }
            }
        }
        
        // Serial number index
        if (certificate.serialNumber) {
            this.indexes.get('serialNumber').delete(certificate.serialNumber);
        }
        
        // Status index
        if (certificate.status) {
            const statusIds = this.indexes.get('status').get(certificate.status);
            if (statusIds) {
                const index = statusIds.indexOf(certificate.id);
                if (index > -1) {
                    statusIds.splice(index, 1);
                }
                if (statusIds.length === 0) {
                    this.indexes.get('status').delete(certificate.status);
                }
            }
        }
        
        // Expiry date index
        if (certificate.notAfter) {
            const expiryKey = new Date(certificate.notAfter).toISOString().split('T')[0];
            const expiryIds = this.indexes.get('expiryDate').get(expiryKey);
            if (expiryIds) {
                const index = expiryIds.indexOf(certificate.id);
                if (index > -1) {
                    expiryIds.splice(index, 1);
                }
                if (expiryIds.length === 0) {
                    this.indexes.get('expiryDate').delete(expiryKey);
                }
            }
        }
        
        // Type index
        if (certificate.type) {
            const typeIds = this.indexes.get('type').get(certificate.type);
            if (typeIds) {
                const index = typeIds.indexOf(certificate.id);
                if (index > -1) {
                    typeIds.splice(index, 1);
                }
                if (typeIds.length === 0) {
                    this.indexes.get('type').delete(certificate.type);
                }
            }
        }
        
        // Tags index
        const metadata = this.metadata.get(certificate.id);
        if (metadata && metadata.tags) {
            metadata.tags.forEach(tag => {
                const tagIds = this.indexes.get('tags').get(tag);
                if (tagIds) {
                    const index = tagIds.indexOf(certificate.id);
                    if (index > -1) {
                        tagIds.splice(index, 1);
                    }
                    if (tagIds.length === 0) {
                        this.indexes.get('tags').delete(tag);
                    }
                }
            });
        }
    }

    /**
     * Update access metadata
     */
    async updateAccessMetadata(certificateId) {
        const metadata = this.metadata.get(certificateId);
        if (metadata) {
            metadata.lastAccessed = new Date().toISOString();
            metadata.accessCount = (metadata.accessCount || 0) + 1;
            this.metadata.set(certificateId, metadata);
        }
    }

    /**
     * Calculate certificate size
     */
    calculateCertificateSize(certificate) {
        return JSON.stringify(certificate).length;
    }

    /**
     * Check if certificate matches filter
     */
    matchesFilter(certificate, filter) {
        for (const [key, value] of Object.entries(filter)) {
            if (certificate[key] !== value) {
                return false;
            }
        }
        return true;
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
     * Clear storage cache
     */
    clearStorageCache() {
        this.cache.clear();
        console.log('Storage cache cleared');
    }

    /**
     * Refresh storage
     */
    async refreshStorage() {
        try {
            await this.loadExistingCertificates();
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('certificateStorageRefreshed', {
                detail: { statistics: this.statistics }
            }));
        } catch (error) {
            console.error('Storage refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the storage module
     */
    destroy() {
        this.isInitialized = false;
        
        this.storage.clear();
        this.metadata.clear();
        this.indexes.clear();
        this.cache.clear();
        this.backupQueue = [];
        this.cleanupQueue = [];
        
        console.log('🧹 Certificate Storage destroyed');
    }
} 