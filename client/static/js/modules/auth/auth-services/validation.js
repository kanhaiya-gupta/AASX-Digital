/**
 * Validation Service - Form Validation and Data Sanitization
 * @description Handles form validation, data sanitization, and security checks
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-services/validation
 */

/**
 * Validation Service
 * @description Provides comprehensive validation and sanitization for authentication forms
 * @class Validation
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class Validation {
    // Private fields
    #isInitialized = false;
    #validationRules = new Map();
    #customValidators = new Map();
    #sanitizers = new Map();
    #config = {};
    #patterns = {};
    #errorMessages = {};
    
    /**
     * Create a Validation instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.strictMode - Enable strict validation mode
     * @param {boolean} options.sanitizeInput - Enable input sanitization
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            strictMode: options.strictMode ?? true,
            sanitizeInput: options.sanitizeInput ?? true,
            debug: options.debug ?? false
        };
        
        // Validation patterns
        this.#patterns = {
            username: /^[a-zA-Z0-9_]{3,20}$/,
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
            name: /^[a-zA-Z\s]{2,50}$/,
            phone: /^[\+]?[1-9][\d]{0,15}$/
        };
        
        // Error messages
        this.#errorMessages = {
            required: 'This field is required',
            invalidFormat: 'Invalid format',
            tooShort: 'Too short',
            tooLong: 'Too long',
            weakPassword: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character',
            usernameTaken: 'Username already taken',
            emailTaken: 'Email already taken',
            invalidCredentials: 'Invalid username or password'
        };
        
        console.log('✅ Validation service created with config:', this.#config);
    }
    
    /**
     * Initialize the validation service
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ Validation service already initialized');
                return true;
            }
            
            console.log('✅ Initializing validation service...');
            
            // Setup default validation rules
            this.#setupDefaultRules();
            
            // Setup default sanitizers
            this.#setupDefaultSanitizers();
            
            // Setup custom validators
            this.#setupCustomValidators();
            
            this.#isInitialized = true;
            console.log('✅ Validation service initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ Validation service initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Setup default validation rules
     * @private
     */
    #setupDefaultRules() {
        // Username validation
        this.#validationRules.set('username', {
            required: true,
            minLength: 3,
            maxLength: 20,
            pattern: this.#patterns.username,
            custom: 'validateUsername'
        });
        
        // Email validation
        this.#validationRules.set('email', {
            required: true,
            pattern: this.#patterns.email,
            custom: 'validateEmail'
        });
        
        // Password validation
        this.#validationRules.set('password', {
            required: true,
            minLength: 8,
            pattern: this.#patterns.password,
            custom: 'validatePassword'
        });
        
        // Confirm password validation
        this.#validationRules.set('confirmPassword', {
            required: true,
            custom: 'validateConfirmPassword'
        });
        
        // Name validation
        this.#validationRules.set('name', {
            required: true,
            minLength: 2,
            maxLength: 50,
            pattern: this.#patterns.name
        });
        
        // Phone validation
        this.#validationRules.set('phone', {
            required: false,
            pattern: this.#patterns.phone
        });
        
        console.log('📋 Default validation rules setup complete');
    }
    
    /**
     * Setup default sanitizers
     * @private
     */
    #setupDefaultSanitizers() {
        // Username sanitizer
        this.#sanitizers.set('username', (value) => {
            return value.trim().toLowerCase().replace(/[^a-z0-9_]/g, '');
        });
        
        // Email sanitizer
        this.#sanitizers.set('email', (value) => {
            return value.trim().toLowerCase();
        });
        
        // Name sanitizer
        this.#sanitizers.set('name', (value) => {
            return value.trim().replace(/\s+/g, ' ').replace(/[^a-zA-Z\s]/g, '');
        });
        
        // Phone sanitizer
        this.#sanitizers.set('phone', (value) => {
            return value.replace(/[^\d+]/g, '');
        });
        
        // General text sanitizer
        this.#sanitizers.set('text', (value) => {
            return value.trim().replace(/[<>]/g, '');
        });
        
        console.log('🧹 Default sanitizers setup complete');
    }
    
    /**
     * Setup custom validators
     * @private
     */
    #setupCustomValidators() {
        // Username availability validator
        this.#customValidators.set('validateUsername', async (value, context) => {
            // This would typically check against the database
            // For now, we'll simulate the check
            if (value === 'admin' || value === 'root') {
                return { valid: false, message: this.#errorMessages.usernameTaken };
            }
            return { valid: true };
        });
        
        // Email availability validator
        this.#customValidators.set('validateEmail', async (value, context) => {
            // This would typically check against the database
            // For now, we'll simulate the check
            if (value === 'admin@example.com' || value === 'root@example.com') {
                return { valid: false, message: this.#errorMessages.emailTaken };
            }
            return { valid: true };
        });
        
        // Password strength validator
        this.#customValidators.set('validatePassword', async (value, context) => {
            const hasLower = /[a-z]/.test(value);
            const hasUpper = /[A-Z]/.test(value);
            const hasNumber = /\d/.test(value);
            const hasSpecial = /[@$!%*?&]/.test(value);
            
            if (!hasLower || !hasUpper || !hasNumber || !hasSpecial) {
                return { valid: false, message: this.#errorMessages.weakPassword };
            }
            
            return { valid: true };
        });
        
        // Confirm password validator
        this.#customValidators.set('validateConfirmPassword', async (value, context) => {
            const password = context?.password || context?.formData?.password;
            if (value !== password) {
                return { valid: false, message: 'Passwords do not match' };
            }
            return { valid: true };
        });
        
        console.log('🔧 Custom validators setup complete');
    }
    
    /**
     * Validate a single field
     * @param {string} fieldName - Field name
     * @param {*} value - Field value
     * @param {Object} context - Validation context
     * @returns {Promise<Object>} Validation result
     */
    async validateField(fieldName, value, context = {}) {
        try {
            const rules = this.#validationRules.get(fieldName);
            if (!rules) {
                return { valid: true, message: null };
            }
            
            // Check if field is required
            if (rules.required && (!value || value.toString().trim() === '')) {
                return { valid: false, message: this.#errorMessages.required };
            }
            
            // Skip validation if field is empty and not required
            if (!value || value.toString().trim() === '') {
                return { valid: true, message: null };
            }
            
            // Sanitize input if enabled
            if (this.#config.sanitizeInput) {
                value = this.sanitizeField(fieldName, value);
            }
            
            // Check minimum length
            if (rules.minLength && value.length < rules.minLength) {
                return { valid: false, message: this.#errorMessages.tooShort };
            }
            
            // Check maximum length
            if (rules.maxLength && value.length > rules.maxLength) {
                return { valid: false, message: this.#errorMessages.tooLong };
            }
            
            // Check pattern
            if (rules.pattern && !rules.pattern.test(value)) {
                return { valid: false, message: this.#errorMessages.invalidFormat };
            }
            
            // Run custom validator
            if (rules.custom) {
                const customValidator = this.#customValidators.get(rules.custom);
                if (customValidator) {
                    const result = await customValidator(value, context);
                    if (!result.valid) {
                        return result;
                    }
                }
            }
            
            return { valid: true, message: null, sanitizedValue: value };
            
        } catch (error) {
            console.error(`❌ Field validation failed for ${fieldName}:`, error);
            return { valid: false, message: 'Validation error occurred' };
        }
    }
    
    /**
     * Validate multiple fields
     * @param {Object} formData - Form data object
     * @param {Array} fields - Array of field names to validate
     * @returns {Promise<Object>} Validation results
     */
    async validateFields(formData, fields = []) {
        try {
            const results = {};
            const errors = {};
            let isValid = true;
            
            // If no fields specified, validate all fields with rules
            if (fields.length === 0) {
                fields = Array.from(this.#validationRules.keys());
            }
            
            for (const fieldName of fields) {
                const value = formData[fieldName];
                const result = await this.validateField(fieldName, value, { formData });
                
                results[fieldName] = result;
                
                if (!result.valid) {
                    errors[fieldName] = result.message;
                    isValid = false;
                }
            }
            
            return {
                isValid,
                results,
                errors,
                sanitizedData: this.#extractSanitizedData(results)
            };
            
        } catch (error) {
            console.error('❌ Fields validation failed:', error);
            return {
                isValid: false,
                results: {},
                errors: { general: 'Validation error occurred' },
                sanitizedData: {}
            };
        }
    }
    
    /**
     * Validate complete form
     * @param {Object} formData - Form data object
     * @returns {Promise<Object>} Form validation result
     */
    async validateForm(formData) {
        try {
            console.log('📝 Validating form data:', formData);
            
            const result = await this.validateFields(formData);
            
            if (result.isValid) {
                console.log('✅ Form validation successful');
            } else {
                console.log('❌ Form validation failed:', result.errors);
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ Form validation failed:', error);
            throw error;
        }
    }
    
    /**
     * Sanitize a single field
     * @param {string} fieldName - Field name
     * @param {*} value - Field value
     * @returns {*} Sanitized value
     */
    sanitizeField(fieldName, value) {
        try {
            if (!value || typeof value !== 'string') {
                return value;
            }
            
            const sanitizer = this.#sanitizers.get(fieldName);
            if (sanitizer) {
                return sanitizer(value);
            }
            
            // Use general text sanitizer as fallback
            const generalSanitizer = this.#sanitizers.get('text');
            if (generalSanitizer) {
                return generalSanitizer(value);
            }
            
            return value;
            
        } catch (error) {
            console.warn(`⚠️ Sanitization failed for ${fieldName}:`, error);
            return value;
        }
    }
    
    /**
     * Sanitize multiple fields
     * @param {Object} formData - Form data object
     * @param {Array} fields - Array of field names to sanitize
     * @returns {Object} Sanitized form data
     */
    sanitizeFields(formData, fields = []) {
        try {
            const sanitized = {};
            
            // If no fields specified, sanitize all fields
            if (fields.length === 0) {
                fields = Object.keys(formData);
            }
            
            for (const fieldName of fields) {
                const value = formData[fieldName];
                sanitized[fieldName] = this.sanitizeField(fieldName, value);
            }
            
            return sanitized;
            
        } catch (error) {
            console.error('❌ Fields sanitization failed:', error);
            return formData;
        }
    }
    
    /**
     * Extract sanitized data from validation results
     * @private
     * @param {Object} results - Validation results
     * @returns {Object} Sanitized data
     */
    #extractSanitizedData(results) {
        const sanitized = {};
        
        for (const [fieldName, result] of Object.entries(results)) {
            if (result.sanitizedValue !== undefined) {
                sanitized[fieldName] = result.sanitizedValue;
            }
        }
        
        return sanitized;
    }
    
    /**
     * Add custom validation rule
     * @param {string} fieldName - Field name
     * @param {Object} rules - Validation rules
     */
    addValidationRule(fieldName, rules) {
        this.#validationRules.set(fieldName, rules);
        console.log(`📋 Added validation rule for ${fieldName}`);
    }
    
    /**
     * Add custom validator
     * @param {string} name - Validator name
     * @param {Function} validator - Validator function
     */
    addCustomValidator(name, validator) {
        this.#customValidators.set(name, validator);
        console.log(`🔧 Added custom validator: ${name}`);
    }
    
    /**
     * Add custom sanitizer
     * @param {string} fieldName - Field name
     * @param {Function} sanitizer - Sanitizer function
     */
    addSanitizer(fieldName, sanitizer) {
        this.#sanitizers.set(fieldName, sanitizer);
        console.log(`🧹 Added sanitizer for ${fieldName}`);
    }
    
    /**
     * Get validation rules for a field
     * @param {string} fieldName - Field name
     * @returns {Object|null} Validation rules
     */
    getValidationRules(fieldName) {
        return this.#validationRules.get(fieldName) || null;
    }
    
    /**
     * Get all validation rules
     * @readonly
     * @returns {Object} All validation rules
     */
    get allValidationRules() {
        return Object.fromEntries(this.#validationRules);
    }
    
    /**
     * Get all patterns
     * @readonly
     * @returns {Object} All validation patterns
     */
    get allPatterns() {
        return { ...this.#patterns };
    }
    
    /**
     * Get all error messages
     * @readonly
     * @returns {Object} All error messages
     */
    get allErrorMessages() {
        return { ...this.#errorMessages };
    }
    
    /**
     * Check if validation service is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get validation service status
     * @returns {Object} Service status
     */
    getValidationStatus() {
        return {
            isInitialized: this.#isInitialized,
            strictMode: this.#config.strictMode,
            sanitizeInput: this.#config.sanitizeInput,
            validationRulesCount: this.#validationRules.size,
            customValidatorsCount: this.#customValidators.size,
            sanitizersCount: this.#sanitizers.size
        };
    }
    
    /**
     * Create a default Validation instance
     * @static
     * @returns {Validation} New instance with default config
     */
    static createDefault() {
        return new Validation({
            strictMode: true,
            sanitizeInput: true,
            debug: false
        });
    }
}
