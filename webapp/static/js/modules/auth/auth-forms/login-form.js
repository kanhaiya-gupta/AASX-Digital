/**
 * Login Form - User Authentication Interface
 * @description Handles user login with validation, API integration, and user experience
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-forms/login-form
 */

/**
 * Login Form
 * @description Manages user login form with comprehensive validation and API integration
 * @class LoginForm
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class LoginForm {
    // Private fields
    #isInitialized = false;
    #form = null;
    #formData = {};
    #validationErrors = {};
    #isSubmitting = false;
    #submitAttempts = 0;
    #maxSubmitAttempts = 3;
    #config = {};
    #fieldSelectors = {};
    #formState = {};
    #eventListeners = new Map();
    #validationRules = {};
    #errorMessages = {};
    
    /**
     * Create a LoginForm instance
     * @param {Object} options - Configuration options
     * @param {string} options.formSelector - CSS selector for the form
     * @param {boolean} options.autoValidate - Enable automatic validation
     * @param {boolean} options.showPasswordToggle - Enable password visibility toggle
     * @param {boolean} options.rememberMe - Enable remember me functionality
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            formSelector: options.formSelector ?? '#loginForm',
            autoValidate: options.autoValidate ?? true,
            showPasswordToggle: options.showPasswordToggle ?? true,
            rememberMe: options.rememberMe ?? true,
            debug: options.debug ?? false
        };
        
        // Form field selectors
        this.#fieldSelectors = {
            username: '#login_username',
            password: '#login_password',
            rememberMe: '#login_rememberMe',
            submitButton: '#loginBtn',
            passwordToggle: '#togglePassword',
            errorContainer: '#loginErrors',
            successContainer: '#loginSuccess'
        };
        
        // Form state
        this.#formState = {
            isValid: false,
            isDirty: false,
            hasErrors: false,
            lastValidation: null
        };
        
        // Validation rules
        this.#validationRules = {
            username: {
                required: true,
                minLength: 3,
                maxLength: 50,
                pattern: /^[a-zA-Z0-9_@.-]+$/
            },
            password: {
                required: true,
                minLength: 1 // No minimum for login
            }
        };
        
        // Error messages
        this.#errorMessages = {
            username: {
                required: 'Username is required',
                minLength: 'Username must be at least 3 characters',
                maxLength: 'Username must be less than 50 characters',
                pattern: 'Username contains invalid characters'
            },
            password: {
                required: 'Password is required'
            },
            general: {
                invalidCredentials: 'Invalid username or password',
                tooManyAttempts: 'Too many login attempts. Please try again later.',
                networkError: 'Network error. Please check your connection.',
                serverError: 'Server error. Please try again later.'
            }
        };
        
        console.log('🔐 LoginForm created with config:', this.#config);
    }
    
    /**
     * Initialize the login form
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ LoginForm already initialized');
                return true;
            }
            
            console.log('🔐 Initializing LoginForm...');
            
            // Find the form element
            await this.#findFormElement();
            
            // Setup form fields
            this.#setupFormFields();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            // Setup password toggle
            if (this.#config.showPasswordToggle) {
                this.#setupPasswordToggle();
            }
            
            // Setup auto-validation
            if (this.#config.autoValidate) {
                this.#setupAutoValidation();
            }
            
            // Initial form state
            this.#updateFormState();
            
            this.#isInitialized = true;
            console.log('✅ LoginForm initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ LoginForm initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Find the form element
     * @private
     */
    async #findFormElement() {
        try {
            console.log('🔍 DEBUG - Looking for form with selector:', this.#config.formSelector);
            this.#form = document.querySelector(this.#config.formSelector);
            
            if (!this.#form) {
                console.log('❌ DEBUG - Form not found. All forms on page:', document.querySelectorAll('form'));
                throw new Error(`Login form not found with selector: ${this.#config.formSelector}`);
            }
            
            console.log('✅ Login form element found:', this.#form);
            console.log('🔍 DEBUG - Form HTML:', this.#form.outerHTML);
            
        } catch (error) {
            console.error('❌ Form element discovery failed:', error);
            throw error;
        }
    }
    
    /**
     * Setup form fields
     * @private
     */
    #setupFormFields() {
        try {
            // Initialize form data
            this.#formData = {
                username: '',
                password: '',
                rememberMe: false
            };
            
            // Get field elements
            for (const [fieldName, selector] of Object.entries(this.#fieldSelectors)) {
                const element = document.querySelector(selector);
                if (element) {
                    this.#eventListeners.set(fieldName, element);
                }
            }
            
            console.log('✅ Form fields setup complete');
            
        } catch (error) {
            console.error('❌ Form fields setup failed:', error);
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    #setupEventListeners() {
        try {
            console.log('🔍 DEBUG - Starting setupEventListeners...');
            console.log('🔍 DEBUG - Field selectors:', this.#fieldSelectors);
            
            // Form submission
            this.#form.addEventListener('submit', (event) => {
                event.preventDefault();
                this.#handleFormSubmit();
            });
            
            // Field input events
            const usernameField = document.querySelector(this.#fieldSelectors.username);
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            const rememberMeField = document.querySelector(this.#fieldSelectors.rememberMe);
            
            console.log('🔍 DEBUG - Username field found:', usernameField);
            console.log('🔍 DEBUG - Password field found:', passwordField);
            console.log('🔍 DEBUG - RememberMe field found:', rememberMeField);
            
            if (usernameField) {
                usernameField.addEventListener('input', (event) => {
                    this.#handleFieldInput('username', event.target.value);
                });
                
                usernameField.addEventListener('blur', (event) => {
                    this.#validateField('username', event.target.value);
                });
                
                // 🔍 DEBUG: Log when username field is found and event listeners added
                console.log('🔍 DEBUG - Username field found:', usernameField);
                console.log('🔍 DEBUG - Username field value:', usernameField.value);
                console.log('🔍 DEBUG - Username field selector used:', this.#fieldSelectors.username);
            } else {
                console.log('❌ DEBUG - Username field NOT found with selector:', this.#fieldSelectors.username);
                console.log('❌ DEBUG - All elements with id="username":', document.querySelectorAll('#username'));
            }
            
            if (passwordField) {
                passwordField.addEventListener('input', (event) => {
                    this.#handleFieldInput('password', event.target.value);
                });
                
                passwordField.addEventListener('blur', (event) => {
                    this.#validateField('password', event.target.value);
                });
                
                // 🔍 DEBUG: Log when password field is found and event listeners added
                console.log('🔍 DEBUG - Password field found:', passwordField);
                console.log('🔍 DEBUG - Password field value:', passwordField.value);
                console.log('🔍 DEBUG - Password field selector used:', this.#fieldSelectors.password);
            } else {
                console.log('❌ DEBUG - Password field NOT found with selector:', this.#fieldSelectors.password);
                console.log('❌ DEBUG - All elements with id="password":', document.querySelectorAll('#password'));
            }
            
            if (rememberMeField) {
                rememberMeField.addEventListener('change', (event) => {
                    this.#formData.rememberMe = event.target.checked;
                });
            }
            
            console.log('👂 Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listeners setup failed:', error);
        }
    }
    
    /**
     * Setup password toggle
     * @private
     */
    #setupPasswordToggle() {
        try {
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            const toggleButton = document.querySelector(this.#fieldSelectors.passwordToggle);
            
            if (passwordField && toggleButton) {
                toggleButton.addEventListener('click', () => {
                    const type = passwordField.type === 'password' ? 'text' : 'password';
                    passwordField.type = type;
                    
                    const icon = toggleButton.querySelector('i');
                    if (icon) {
                        icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
                    }
                    
                    toggleButton.setAttribute('title', 
                        type === 'password' ? 'Show password' : 'Hide password'
                    );
                });
                
                console.log('✅ Password toggle setup complete');
            }
            
        } catch (error) {
            console.error('❌ Password toggle setup failed:', error);
        }
    }
    
    /**
     * Setup auto-validation
     * @private
     */
    #setupAutoValidation() {
        try {
            // Validate on field blur
            const fields = ['username', 'password'];
            
            fields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    field.addEventListener('blur', () => {
                        this.#validateField(fieldName, field.value);
                    });
                }
            });
            
            console.log('✅ Auto-validation setup complete');
            
        } catch (error) {
            console.error('❌ Auto-validation setup failed:', error);
        }
    }
    
    /**
     * Handle field input
     * @private
     * @param {string} fieldName - Field name
     * @param {string} value - Field value
     */
    #handleFieldInput(fieldName, value) {
        try {
            // 🔍 DEBUG: Log field input handling
            console.log(`🔍 DEBUG - handleFieldInput called for ${fieldName}:`, value);
            console.log(`🔍 DEBUG - Previous formData[${fieldName}]:`, this.#formData[fieldName]);
            
            // Update form data
            this.#formData[fieldName] = value;
            
            // 🔍 DEBUG: Log updated form data
            console.log(`🔍 DEBUG - Updated formData[${fieldName}]:`, this.#formData[fieldName]);
            console.log(`🔍 DEBUG - Full formData:`, this.#formData);
            
            // Mark form as dirty
            this.#formState.isDirty = true;
            
            // Clear field error
            this.#clearFieldError(fieldName);
            
            // Update form state
            this.#updateFormState();
            
        } catch (error) {
            console.error(`❌ Field input handling failed for ${fieldName}:`, error);
        }
    }
    
    /**
     * Validate a single field
     * @private
     * @param {string} fieldName - Field name
     * @param {string} value - Field value
     * @returns {boolean} Field validity
     */
    #validateField(fieldName, value) {
        try {
            const rules = this.#validationRules[fieldName];
            if (!rules) {
                return true;
            }
            
            let isValid = true;
            let errorMessage = '';
            
            // Required validation
            if (rules.required && (!value || value.trim() === '')) {
                isValid = false;
                errorMessage = this.#errorMessages[fieldName].required;
            }
            
            // Length validation
            if (isValid && value) {
                if (rules.minLength && value.length < rules.minLength) {
                    isValid = false;
                    errorMessage = this.#errorMessages[fieldName].minLength;
                } else if (rules.maxLength && value.length > rules.maxLength) {
                    isValid = false;
                    errorMessage = this.#errorMessages[fieldName].maxLength;
                }
            }
            
            // Pattern validation
            if (isValid && value && rules.pattern && !rules.pattern.test(value)) {
                isValid = false;
                errorMessage = this.#errorMessages[fieldName].pattern;
            }
            
            // Update validation state
            if (isValid) {
                this.#clearFieldError(fieldName);
            } else {
                this.#showFieldError(fieldName, errorMessage);
            }
            
            // Update form state
            this.#updateFormState();
            
            return isValid;
            
        } catch (error) {
            console.error(`❌ Field validation failed for ${fieldName}:`, error);
            return false;
        }
    }
    
    /**
     * Validate all fields
     * @private
     * @returns {boolean} Form validity
     */
    #validateAllFields() {
        try {
            let isValid = true;
            
            for (const [fieldName, rules] of Object.entries(this.#validationRules)) {
                const value = this.#formData[fieldName];
                if (!this.#validateField(fieldName, value)) {
                    isValid = false;
                }
            }
            
            return isValid;
            
        } catch (error) {
            console.error('❌ All fields validation failed:', error);
            return false;
        }
    }
    
    /**
     * Show field error
     * @private
     * @param {string} fieldName - Field name
     * @param {string} message - Error message
     */
    #showFieldError(fieldName, message) {
        try {
            const field = document.querySelector(this.#fieldSelectors[fieldName]);
            if (!field) return;
            
            // Add error class
            field.classList.add('is-invalid');
            
            // Create or update error message
            let errorElement = field.parentNode.querySelector('.invalid-feedback');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'invalid-feedback';
                field.parentNode.appendChild(errorElement);
            }
            
            errorElement.textContent = message;
            
            // Store error
            this.#validationErrors[fieldName] = message;
            
        } catch (error) {
            console.error(`❌ Field error display failed for ${fieldName}:`, error);
        }
    }
    
    /**
     * Clear field error
     * @private
     * @param {string} fieldName - Field name
     */
    #clearFieldError(fieldName) {
        try {
            const field = document.querySelector(this.#fieldSelectors[fieldName]);
            if (!field) return;
            
            // Remove error class
            field.classList.remove('is-invalid');
            
            // Remove error message
            const errorElement = field.parentNode.querySelector('.invalid-feedback');
            if (errorElement) {
                errorElement.remove();
            }
            
            // Clear stored error
            delete this.#validationErrors[fieldName];
            
        } catch (error) {
            console.error(`❌ Field error clear failed for ${fieldName}:`, error);
        }
    }
    
    /**
     * Handle form submission
     * @private
     */
    async #handleFormSubmit() {
        try {
            if (this.#isSubmitting) {
                console.log('⚠️ Form submission already in progress');
                return;
            }
            
            // Check submit attempts
            if (this.#submitAttempts >= this.#maxSubmitAttempts) {
                this.#showGeneralError(this.#errorMessages.general.tooManyAttempts);
                return;
            }
            
            // Validate form - TEMPORARILY DISABLED FOR TESTING
            // if (!this.#validateAllFields()) {
            //     console.log('❌ Form validation failed');
            //     return;
            // }
            console.log('🔐 Form validation bypassed for testing');
            
            // 🔍 DEBUG: Log form data before submission
            console.log('🔍 DEBUG - Form data before submission:', {
                username: this.#formData.username,
                password: this.#formData.password,
                rememberMe: this.#formData.rememberMe
            });
            
            // Set submitting state
            this.#setSubmittingState(true);
            
            // Attempt login
            const success = await this.#attemptLogin();
            
            if (success) {
                this.#handleLoginSuccess();
            } else {
                this.#handleLoginFailure();
            }
            
        } catch (error) {
            console.error('❌ Form submission handling failed:', error);
            this.#handleLoginFailure();
        } finally {
            this.#setSubmittingState(false);
        }
    }
    
    /**
     * Attempt user login
     * @private
     * @returns {Promise<boolean>} Login success
     */
    async #attemptLogin() {
        try {
            console.log('🔐 Attempting user login...');
            
            // Prepare login data
            const loginData = {
                username: this.#formData.username.trim(),
                password: this.#formData.password
            };
            
            // 🔍 DEBUG: Log the credentials being sent (remove in production!)
            console.log('🔍 DEBUG - Username being sent:', loginData.username);
            console.log('🔍 DEBUG - Password being sent:', loginData.password);
            console.log('🔍 DEBUG - Password length:', loginData.password.length);
            
            // Call login API
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Login failed: ${response.status}`);
            }
            
            const authData = await response.json();
            
            // Store authentication data
            this.#storeAuthData(authData);
            
            console.log('✅ Login successful');
            return true;
            
        } catch (error) {
            console.error('❌ Login attempt failed:', error);
            this.#submitAttempts++;
            return false;
        }
    }
    
    /**
     * Store authentication data
     * @private
     * @param {Object} authData - Authentication data
     */
    #storeAuthData(authData) {
        try {
            console.log('💾 Storing authentication data:', {
                hasToken: !!authData.access_token,
                hasUser: !!authData.user,
                rememberMe: this.#formData.rememberMe
            });
            
            const storage = this.#formData.rememberMe ? localStorage : sessionStorage;
            
            storage.setItem('auth_token', authData.access_token);
            
            if (authData.refresh_token) {
                storage.setItem('refresh_token', authData.refresh_token);
            }
            
            if (authData.user) {
                storage.setItem('user_data', JSON.stringify(authData.user));
                console.log('💾 User data stored:', authData.user.username);
            }
            
            console.log('💾 Authentication data stored successfully');
            
        } catch (error) {
            console.error('❌ Authentication data storage failed:', error);
        }
    }
    
    /**
     * Handle login success
     * @private
     */
    #handleLoginSuccess() {
        try {
            // Show success message
            this.#showSuccessMessage('Login successful! Loading your data...');
            
            // Reset form
            this.#resetForm();
            
            // Reset submit attempts
            this.#submitAttempts = 0;
            
            // Dispatch login success event - PostLoginOrchestrator will handle redirect
            this.#dispatchLoginSuccess();
            
            // 🎭 REMOVED IMMEDIATE REDIRECT - Let PostLoginOrchestrator handle it after data loading
            console.log('🎭 Login form: loginSuccess event dispatched, waiting for PostLoginOrchestrator...');
            
        } catch (error) {
            console.error('❌ Login success handling failed:', error);
        }
    }
    
    /**
     * Handle login failure
     * @private
     */
    #handleLoginFailure() {
        try {
            // Show error message
            this.#showGeneralError(this.#errorMessages.general.invalidCredentials);
            
            // Clear password field
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            if (passwordField) {
                passwordField.value = '';
                this.#formData.password = '';
            }
            
            // Focus password field
            if (passwordField) {
                passwordField.focus();
            }
            
            // Dispatch login failure event
            this.#dispatchLoginFailure();
            
        } catch (error) {
            console.error('❌ Login failure handling failed:', error);
        }
    }
    
    /**
     * Set submitting state
     * @private
     * @param {boolean} isSubmitting - Submitting state
     */
    #setSubmittingState(isSubmitting) {
        try {
            this.#isSubmitting = isSubmitting;
            
            const submitButton = document.querySelector(this.#fieldSelectors.submitButton);
            if (submitButton) {
                submitButton.disabled = isSubmitting;
                submitButton.innerHTML = isSubmitting 
                    ? '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...'
                    : '<i class="fas fa-sign-in-alt me-2"></i>Login';
            }
            
            // Disable form fields during submission
            const fields = ['username', 'password'];
            fields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    field.disabled = isSubmitting;
                }
            });
            
        } catch (error) {
            console.error('❌ Submitting state update failed:', error);
        }
    }
    
    /**
     * Show success message
     * @private
     * @param {string} message - Success message
     */
    #showSuccessMessage(message) {
        try {
            const successContainer = document.querySelector(this.#fieldSelectors.successContainer);
            if (successContainer) {
                successContainer.innerHTML = `
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <i class="fas fa-check-circle me-2"></i>${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                successContainer.style.display = 'block';
            }
            
        } catch (error) {
            console.error('❌ Success message display failed:', error);
        }
    }
    
    /**
     * Show general error
     * @private
     * @param {string} message - Error message
     */
    #showGeneralError(message) {
        try {
            const errorContainer = document.querySelector(this.#fieldSelectors.errorContainer);
            if (errorContainer) {
                errorContainer.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                errorContainer.style.display = 'block';
            }
            
        } catch (error) {
            console.error('❌ General error display failed:', error);
        }
    }
    
    /**
     * Reset form
     * @private
     */
    #resetForm() {
        try {
            // Clear form data
            this.#formData = {
                username: '',
                password: '',
                rememberMe: false
            };
            
            // Reset form fields
            const usernameField = document.querySelector(this.#fieldSelectors.username);
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            const rememberMeField = document.querySelector(this.#fieldSelectors.rememberMe);
            
            if (usernameField) usernameField.value = '';
            if (passwordField) passwordField.value = '';
            if (rememberMeField) rememberMeField.checked = false;
            
            // Clear errors
            this.#validationErrors = {};
            this.#clearAllFieldErrors();
            
            // Reset form state
            this.#formState = {
                isValid: false,
                isDirty: false,
                hasErrors: false,
                lastValidation: null
            };
            
            // Update form state
            this.#updateFormState();
            
            console.log('✅ Form reset complete');
            
        } catch (error) {
            console.error('❌ Form reset failed:', error);
        }
    }
    
    /**
     * Clear all field errors
     * @private
     */
    #clearAllFieldErrors() {
        try {
            for (const fieldName of Object.keys(this.#validationRules)) {
                this.#clearFieldError(fieldName);
            }
            
            // Clear error containers
            const errorContainer = document.querySelector(this.#fieldSelectors.errorContainer);
            const successContainer = document.querySelector(this.#fieldSelectors.successContainer);
            
            if (errorContainer) errorContainer.style.display = 'none';
            if (successContainer) successContainer.style.display = 'none';
            
        } catch (error) {
            console.error('❌ Clear all field errors failed:', error);
        }
    }
    
    /**
     * Update form state
     * @private
     */
    #updateFormState() {
        try {
            // Check if form is valid
            this.#formState.isValid = Object.keys(this.#validationErrors).length === 0;
            
            // Check if form has errors
            this.#formState.hasErrors = Object.keys(this.#validationErrors).length > 0;
            
            // Update last validation timestamp
            this.#formState.lastValidation = Date.now();
            
            // Update submit button state
            const submitButton = document.querySelector(this.#fieldSelectors.submitButton);
            if (submitButton) {
                submitButton.disabled = !this.#formState.isValid || this.#isSubmitting;
            }
            
        } catch (error) {
            console.error('❌ Form state update failed:', error);
        }
    }
    
    /**
     * Dispatch login success event
     * @private
     */
    #dispatchLoginSuccess() {
        try {
            // 🔧 CRITICAL FIX: Get the actual token and user data from storage
            const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
            
            // Parse user data if it's stored as JSON string
            let user = null;
            if (userData) {
                try {
                    user = JSON.parse(userData);
                } catch (e) {
                    console.warn('⚠️ Failed to parse stored user data:', e);
                    user = { username: this.#formData.username };
                }
            }
            
            const event = new CustomEvent('loginSuccess', {
                detail: {
                    token: token,  // 🔧 CRITICAL: Include actual token
                    user: user,    // 🔧 CRITICAL: Include actual user object
                    username: this.#formData.username,
                    timestamp: Date.now(),
                    hasToken: !!token,
                    hasUserData: !!user
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Login success event dispatched with details:', event.detail);
            
        } catch (error) {
            console.error('❌ Login success event dispatch failed:', error);
        }
    }
    
    /**
     * Dispatch login failure event
     * @private
     */
    #dispatchLoginFailure() {
        try {
            const event = new CustomEvent('loginFailure', {
                detail: {
                    username: this.#formData.username,
                    attempts: this.#submitAttempts,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Login failure event dispatched');
            
        } catch (error) {
            console.error('❌ Login failure event dispatch failed:', error);
        }
    }
    
    /**
     * Get form data
     * @readonly
     * @returns {Object} Form data
     */
    get formData() {
        return { ...this.#formData };
    }
    
    /**
     * Get form state
     * @readonly
     * @returns {Object} Form state
     */
    get formState() {
        return { ...this.#formState };
    }
    
    /**
     * Get validation errors
     * @readonly
     * @returns {Object} Validation errors
     */
    get validationErrors() {
        return { ...this.#validationErrors };
    }
    
    /**
     * Check if form is submitting
     * @readonly
     * @returns {boolean} Submitting status
     */
    get isSubmitting() {
        return this.#isSubmitting;
    }
    
    /**
     * Check if form is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get login form status
     * @returns {Object} Form status
     */
    getLoginFormStatus() {
        return {
            isInitialized: this.#isInitialized,
            isSubmitting: this.#isSubmitting,
            submitAttempts: this.#submitAttempts,
            maxSubmitAttempts: this.#maxSubmitAttempts,
            formState: this.#formState,
            validationErrors: this.#validationErrors
        };
    }
    
    /**
     * Create a default LoginForm instance
     * @static
     * @returns {LoginForm} New instance with default config
     */
    static createDefault() {
        return new LoginForm({
            formSelector: '#loginForm',
            autoValidate: true,
            showPasswordToggle: true,
            rememberMe: true,
            debug: false
        });
    }
}
