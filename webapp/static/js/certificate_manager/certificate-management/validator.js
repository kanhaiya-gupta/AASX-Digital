/**
 * Certificate Validator Module
 * Handles certificate validation, verification, and security checks
 */

export default class CertificateValidator {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/certificate-manager',
            validationEnabled: true,
            ocspEnabled: true,
            crlEnabled: true,
            signatureValidation: true,
            expiryValidation: true,
            chainValidation: true,
            keyUsageValidation: true,
            extendedKeyUsageValidation: true,
            subjectAltNameValidation: true,
            maxValidationTime: 30000, // 30 seconds
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            retryAttempts: 3,
            retryDelay: 1000
        };

        this.validators = new Map();
        this.validationCache = new Map();
        this.ocspCache = new Map();
        this.crlCache = new Map();
        this.validationQueue = [];
        this.isProcessing = false;
        this.statistics = {
            totalValidations: 0,
            successfulValidations: 0,
            failedValidations: 0,
            ocspChecks: 0,
            crlChecks: 0,
            cacheHits: 0,
            cacheMisses: 0,
            lastValidation: null
        };
    }

    /**
     * Initialize the Certificate Validator
     */
    async init() {
        console.log('🔧 Initializing Certificate Validator...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize validators
            this.initializeValidators();

            // Initialize validation cache
            if (this.config.cacheEnabled) {
                this.initializeValidationCache();
            }

            // Start validation queue
            this.startValidationQueue();

            this.isInitialized = true;
            console.log('✅ Certificate Validator initialized');

        } catch (error) {
            console.error('❌ Certificate Validator initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validator-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load validator configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize validators
     */
    initializeValidators() {
        // Format validator
        this.validators.set('format', {
            validate: (certificate) => this.validateFormat(certificate),
            name: 'Certificate Format Validation'
        });

        // Signature validator
        this.validators.set('signature', {
            validate: (certificate) => this.validateSignature(certificate),
            name: 'Certificate Signature Validation'
        });

        // Expiry validator
        this.validators.set('expiry', {
            validate: (certificate) => this.validateExpiry(certificate),
            name: 'Certificate Expiry Validation'
        });

        // Chain validator
        this.validators.set('chain', {
            validate: (certificate) => this.validateChain(certificate),
            name: 'Certificate Chain Validation'
        });

        // Key usage validator
        this.validators.set('keyUsage', {
            validate: (certificate) => this.validateKeyUsage(certificate),
            name: 'Key Usage Validation'
        });

        // Extended key usage validator
        this.validators.set('extendedKeyUsage', {
            validate: (certificate) => this.validateExtendedKeyUsage(certificate),
            name: 'Extended Key Usage Validation'
        });

        // Subject alternative name validator
        this.validators.set('subjectAltName', {
            validate: (certificate) => this.validateSubjectAltName(certificate),
            name: 'Subject Alternative Name Validation'
        });

        // OCSP validator
        this.validators.set('ocsp', {
            validate: (certificate) => this.validateOCSP(certificate),
            name: 'OCSP Validation'
        });

        // CRL validator
        this.validators.set('crl', {
            validate: (certificate) => this.validateCRL(certificate),
            name: 'CRL Validation'
        });
    }

    /**
     * Initialize validation cache
     */
    initializeValidationCache() {
        // Set up cache cleanup interval
        setInterval(() => {
            this.cleanupValidationCache();
        }, this.config.cacheExpiry);
    }

    /**
     * Start validation queue
     */
    startValidationQueue() {
        setInterval(() => {
            this.processValidationQueue();
        }, 1000);
    }

    /**
     * Validate certificate format
     */
    async validateFormat(certificate) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/format`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Format validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Format validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Certificate format validation failed'
            };
        }
    }

    /**
     * Validate certificate signature
     */
    async validateSignature(certificate) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/signature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Signature validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Signature validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Certificate signature validation failed'
            };
        }
    }

    /**
     * Validate certificate expiry
     */
    async validateExpiry(certificate) {
        try {
            const now = new Date();
            const notBefore = new Date(certificate.notBefore);
            const notAfter = new Date(certificate.notAfter);

            const isNotYetValid = now < notBefore;
            const isExpired = now > notAfter;
            const daysUntilExpiry = Math.ceil((notAfter - now) / (1000 * 60 * 60 * 24));

            return {
                valid: !isNotYetValid && !isExpired,
                isNotYetValid,
                isExpired,
                daysUntilExpiry,
                notBefore: certificate.notBefore,
                notAfter: certificate.notAfter,
                details: isNotYetValid ? 'Certificate is not yet valid' :
                         isExpired ? 'Certificate has expired' :
                         `Certificate is valid for ${daysUntilExpiry} more days`
            };
        } catch (error) {
            console.error('Expiry validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Certificate expiry validation failed'
            };
        }
    }

    /**
     * Validate certificate chain
     */
    async validateChain(certificate) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/chain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Chain validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Chain validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Certificate chain validation failed'
            };
        }
    }

    /**
     * Validate key usage
     */
    async validateKeyUsage(certificate, requiredKeyUsages = []) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/key-usage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate, requiredKeyUsages })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Key usage validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Key usage validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Key usage validation failed'
            };
        }
    }

    /**
     * Validate extended key usage
     */
    async validateExtendedKeyUsage(certificate, requiredExtendedKeyUsages = []) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/extended-key-usage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate, requiredExtendedKeyUsages })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Extended key usage validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Extended key usage validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Extended key usage validation failed'
            };
        }
    }

    /**
     * Validate subject alternative name
     */
    async validateSubjectAltName(certificate, expectedNames = []) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/subject-alt-name`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate, expectedNames })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Subject alternative name validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Subject alternative name validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Subject alternative name validation failed'
            };
        }
    }

    /**
     * Validate OCSP (Online Certificate Status Protocol)
     */
    async validateOCSP(certificate) {
        const cacheKey = `ocsp:${certificate.serialNumber}`;
        
        // Check cache first
        const cached = this.ocspCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            this.statistics.cacheHits++;
            return cached.result;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/ocsp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Cache result
                this.ocspCache.set(cacheKey, {
                    result,
                    timestamp: Date.now()
                });

                this.statistics.ocspChecks++;
                this.statistics.cacheMisses++;
                
                return result;
            } else {
                throw new Error(`OCSP validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('OCSP validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'OCSP validation failed'
            };
        }
    }

    /**
     * Validate CRL (Certificate Revocation List)
     */
    async validateCRL(certificate) {
        const cacheKey = `crl:${certificate.issuer}`;
        
        // Check cache first
        const cached = this.crlCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            this.statistics.cacheHits++;
            return cached.result;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/crl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Cache result
                this.crlCache.set(cacheKey, {
                    result,
                    timestamp: Date.now()
                });

                this.statistics.crlChecks++;
                this.statistics.cacheMisses++;
                
                return result;
            } else {
                throw new Error(`CRL validation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('CRL validation error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'CRL validation failed'
            };
        }
    }

    /**
     * Validate certificate comprehensively
     */
    async validateCertificate(certificate, options = {}) {
        const cacheKey = `validation:${certificate.id || certificate.serialNumber}`;
        
        // Check cache first
        const cached = this.validationCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            this.statistics.cacheHits++;
            return cached.result;
        }

        this.statistics.cacheMisses++;
        this.statistics.totalValidations++;

        const validationOptions = {
            format: this.config.validationEnabled,
            signature: this.config.signatureValidation,
            expiry: this.config.expiryValidation,
            chain: this.config.chainValidation,
            keyUsage: this.config.keyUsageValidation,
            extendedKeyUsage: this.config.extendedKeyUsageValidation,
            subjectAltName: this.config.subjectAltNameValidation,
            ocsp: this.config.ocspEnabled,
            crl: this.config.crlEnabled,
            ...options
        };

        const results = {
            certificateId: certificate.id,
            serialNumber: certificate.serialNumber,
            subject: certificate.subject,
            issuer: certificate.issuer,
            validations: {},
            overallValid: true,
            errors: [],
            warnings: [],
            timestamp: new Date().toISOString()
        };

        // Run all enabled validations
        for (const [validationType, validator] of this.validators) {
            if (validationOptions[validationType]) {
                try {
                    const result = await validator.validate(certificate);
                    results.validations[validationType] = result;
                    
                    if (!result.valid) {
                        results.overallValid = false;
                        results.errors.push({
                            type: validationType,
                            message: result.error || result.details,
                            details: result
                        });
                    } else if (result.warning) {
                        results.warnings.push({
                            type: validationType,
                            message: result.warning,
                            details: result
                        });
                    }
                } catch (error) {
                    results.validations[validationType] = {
                        valid: false,
                        error: error.message
                    };
                    results.overallValid = false;
                    results.errors.push({
                        type: validationType,
                        message: error.message,
                        details: error
                    });
                }
            }
        }

        // Update statistics
        if (results.overallValid) {
            this.statistics.successfulValidations++;
        } else {
            this.statistics.failedValidations++;
        }
        this.statistics.lastValidation = new Date().toISOString();

        // Cache result
        this.validationCache.set(cacheKey, {
            result: results,
            timestamp: Date.now()
        });

        // Dispatch event
        window.dispatchEvent(new CustomEvent('certificateValidated', {
            detail: { certificate, results }
        }));

        return results;
    }

    /**
     * Validate multiple certificates
     */
    async validateCertificates(certificates, options = {}) {
        const results = [];
        
        for (const certificate of certificates) {
            try {
                const result = await this.validateCertificate(certificate, options);
                results.push(result);
            } catch (error) {
                results.push({
                    certificateId: certificate.id,
                    serialNumber: certificate.serialNumber,
                    overallValid: false,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }

        return results;
    }

    /**
     * Validate certificate for specific use case
     */
    async validateForUseCase(certificate, useCase) {
        const useCaseValidations = {
            'ssl': {
                keyUsage: ['keyEncipherment', 'digitalSignature'],
                extendedKeyUsage: ['serverAuth'],
                subjectAltName: true
            },
            'client': {
                keyUsage: ['digitalSignature'],
                extendedKeyUsage: ['clientAuth']
            },
            'code-signing': {
                keyUsage: ['digitalSignature'],
                extendedKeyUsage: ['codeSigning']
            },
            'email': {
                keyUsage: ['digitalSignature', 'keyEncipherment'],
                extendedKeyUsage: ['emailProtection']
            }
        };

        const validationOptions = useCaseValidations[useCase];
        if (!validationOptions) {
            throw new Error(`Unknown use case: ${useCase}`);
        }

        return await this.validateCertificate(certificate, validationOptions);
    }

    /**
     * Check certificate revocation status
     */
    async checkRevocationStatus(certificate) {
        const results = {
            certificateId: certificate.id,
            serialNumber: certificate.serialNumber,
            ocsp: null,
            crl: null,
            isRevoked: false,
            revocationReason: null,
            timestamp: new Date().toISOString()
        };

        // Check OCSP
        if (this.config.ocspEnabled) {
            try {
                results.ocsp = await this.validateOCSP(certificate);
                if (results.ocsp.revoked) {
                    results.isRevoked = true;
                    results.revocationReason = results.ocsp.revocationReason;
                }
            } catch (error) {
                results.ocsp = { error: error.message };
            }
        }

        // Check CRL
        if (this.config.crlEnabled) {
            try {
                results.crl = await this.validateCRL(certificate);
                if (results.crl.revoked) {
                    results.isRevoked = true;
                    results.revocationReason = results.crl.revocationReason;
                }
            } catch (error) {
                results.crl = { error: error.message };
            }
        }

        return results;
    }

    /**
     * Verify certificate chain
     */
    async verifyCertificateChain(certificate, chain = []) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/validate/verify-chain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ certificate, chain })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Chain verification failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Chain verification error:', error);
            return {
                valid: false,
                error: error.message,
                details: 'Certificate chain verification failed'
            };
        }
    }

    /**
     * Process validation queue
     */
    async processValidationQueue() {
        if (this.isProcessing || this.validationQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.validationQueue.splice(0, 5);
            
            for (const validation of batch) {
                try {
                    const result = await this.validateCertificate(validation.certificate, validation.options);
                    validation.resolve(result);
                } catch (error) {
                    validation.reject(error);
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Add validation to queue
     */
    addToValidationQueue(certificate, options = {}) {
        return new Promise((resolve, reject) => {
            this.validationQueue.push({
                certificate,
                options,
                resolve,
                reject
            });
        });
    }

    /**
     * Cleanup validation cache
     */
    cleanupValidationCache() {
        const now = Date.now();
        
        // Cleanup validation cache
        for (const [key, value] of this.validationCache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.validationCache.delete(key);
            }
        }
        
        // Cleanup OCSP cache
        for (const [key, value] of this.ocspCache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.ocspCache.delete(key);
            }
        }
        
        // Cleanup CRL cache
        for (const [key, value] of this.crlCache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.crlCache.delete(key);
            }
        }
    }

    /**
     * Get validation statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Clear validation cache
     */
    clearValidationCache() {
        this.validationCache.clear();
        this.ocspCache.clear();
        this.crlCache.clear();
        console.log('Validation cache cleared');
    }

    /**
     * Refresh validation
     */
    async refreshValidation() {
        try {
            // Clear cache to force fresh validations
            this.clearValidationCache();
            
            // Reset statistics
            this.statistics = {
                totalValidations: 0,
                successfulValidations: 0,
                failedValidations: 0,
                ocspChecks: 0,
                crlChecks: 0,
                cacheHits: 0,
                cacheMisses: 0,
                lastValidation: null
            };
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('certificateValidationRefreshed'));
        } catch (error) {
            console.error('Validation refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the validator
     */
    destroy() {
        this.isInitialized = false;
        
        this.validators.clear();
        this.validationCache.clear();
        this.ocspCache.clear();
        this.crlCache.clear();
        this.validationQueue = [];
        
        console.log('🧹 Certificate Validator destroyed');
    }
} 