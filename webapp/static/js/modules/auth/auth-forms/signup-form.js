/**
 * Signup Form - User Registration Interface
 * @description Handles user registration with comprehensive validation and password strength checking
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-forms/signup-form
 */

/**
 * Signup Form
 * @description Manages user registration form with comprehensive validation and API integration
 * @class SignupForm
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class SignupForm {
    // Private fields
    #isInitialized = false;
    #form = null;
    #formData = {};
    #validationErrors = {};
    #isSubmitting = false;
    #passwordStrength = 0;
    #passwordSuggestions = [];
    #config = {};
    #fieldSelectors = {};
    #formState = {};
    #eventListeners = new Map();
    #validationRules = {};
    #errorMessages = {};
    #passwordStrengthLevels = {};
    
    /**
     * Create a SignupForm instance
     * @param {Object} options - Configuration options
     * @param {string} options.formSelector - CSS selector for the form
     * @param {boolean} options.autoValidate - Enable automatic validation
     * @param {boolean} options.showPasswordStrength - Enable password strength indicator
     * @param {boolean} options.requireTerms - Require terms and conditions acceptance
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            formSelector: options.formSelector ?? '#signupForm',
            autoValidate: options.autoValidate ?? true,
            showPasswordStrength: options.showPasswordStrength ?? true,
            requireTerms: options.requireTerms ?? true,
            debug: options.debug ?? false
        };
        
        // Form field selectors
        this.#fieldSelectors = {
            username: '#username',
            email: '#email',
            firstName: '#firstName',
            lastName: '#lastName',
            password: '#password',
            confirmPassword: '#confirmPassword',
            termsAccepted: '#termsAccepted',
            submitButton: '#signupSubmit',
            passwordStrength: '#passwordStrength',
            passwordSuggestions: '#passwordSuggestions',
            errorContainer: '#signupErrors',
            successContainer: '#signupSuccess'
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
                maxLength: 30,
                pattern: /^[a-zA-Z0-9_]+$/,
                unique: true
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                unique: true
            },
            firstName: {
                required: true,
                minLength: 2,
                maxLength: 50,
                pattern: /^[a-zA-Z\s'-]+$/
            },
            lastName: {
                required: true,
                minLength: 2,
                maxLength: 50,
                pattern: /^[a-zA-Z\s'-]+$/
            },
            password: {
                required: true,
                minLength: 8,
                maxLength: 128,
                requireUppercase: true,
                requireLowercase: true,
                requireNumbers: true,
                requireSpecialChars: true
            },
            confirmPassword: {
                required: true,
                matchPassword: true
            },
            termsAccepted: {
                required: true
            }
        };
        
        // Error messages
        this.#errorMessages = {
            username: {
                required: 'Username is required',
                minLength: 'Username must be at least 3 characters',
                maxLength: 'Username must be less than 30 characters',
                pattern: 'Username can only contain letters, numbers, and underscores',
                unique: 'Username is already taken'
            },
            email: {
                required: 'Email is required',
                pattern: 'Please enter a valid email address',
                unique: 'Email is already registered'
            },
            firstName: {
                required: 'First name is required',
                minLength: 'First name must be at least 2 characters',
                maxLength: 'First name must be less than 50 characters',
                pattern: 'First name can only contain letters, spaces, hyphens, and apostrophes'
            },
            lastName: {
                required: 'Last name is required',
                minLength: 'Last name must be at least 2 characters',
                maxLength: 'Last name must be less than 50 characters',
                pattern: 'Last name can only contain letters, spaces, hyphens, and apostrophes'
            },
            password: {
                required: 'Password is required',
                minLength: 'Password must be at least 8 characters',
                maxLength: 'Password must be less than 128 characters',
                requireUppercase: 'Password must contain at least one uppercase letter',
                requireLowercase: 'Password must contain at least one lowercase letter',
                requireNumbers: 'Password must contain at least one number',
                requireSpecialChars: 'Password must contain at least one special character'
            },
            confirmPassword: {
                required: 'Please confirm your password',
                matchPassword: 'Passwords do not match'
            },
            termsAccepted: {
                required: 'You must accept the terms and conditions'
            }
        };
        
        // Password strength levels
        this.#passwordStrengthLevels = {
            0: { label: 'Very Weak', class: 'text-danger', width: '20%' },
            1: { label: 'Weak', class: 'text-warning', width: '40%' },
            2: { label: 'Fair', class: 'text-warning', width: '60%' },
            3: { label: 'Good', class: 'text-info', width: '80%' },
            4: { label: 'Strong', class: 'text-success', width: '100%' }
        };
        
        console.log('📝 SignupForm created with config:', this.#config);
    }
    
    /**
     * Initialize the signup form
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ SignupForm already initialized');
                return true;
            }
            
            console.log('📝 Initializing SignupForm...');
            
            // Find the form element
            await this.#findFormElement();
            
            // Setup form fields
            this.#setupFormFields();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            // Setup password strength indicator
            if (this.#config.showPasswordStrength) {
                this.#setupPasswordStrengthIndicator();
            }
            
            // Setup auto-validation
            if (this.#config.autoValidate) {
                this.#setupAutoValidation();
            }
            
            // Initial form state
            this.#updateFormState();
            
            this.#isInitialized = true;
            console.log('✅ SignupForm initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ SignupForm initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Find the form element
     * @private
     */
    async #findFormElement() {
        try {
            this.#form = document.querySelector(this.#config.formSelector);
            
            if (!this.#form) {
                throw new Error(`Signup form not found with selector: ${this.#config.formSelector}`);
            }
            
            console.log('✅ Signup form element found');
            
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
                email: '',
                firstName: '',
                lastName: '',
                password: '',
                confirmPassword: '',
                termsAccepted: false
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
            // Form submission
            this.#form.addEventListener('submit', (event) => {
                event.preventDefault();
                this.#handleFormSubmit();
            });
            
            // Field input events
            const fields = ['username', 'email', 'firstName', 'lastName', 'password', 'confirmPassword'];
            
            fields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    field.addEventListener('input', (event) => {
                        this.#handleFieldInput(fieldName, event.target.value);
                    });
                    
                    field.addEventListener('blur', (event) => {
                        this.#validateField(fieldName, event.target.value);
                    });
                }
            });
            
            // Terms acceptance
            const termsField = document.querySelector(this.#fieldSelectors.termsAccepted);
            if (termsField) {
                termsField.addEventListener('change', (event) => {
                    this.#formData.termsAccepted = event.target.checked;
                    this.#validateField('termsAccepted', event.target.checked);
                });
            }
            
            console.log('👂 Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listeners setup failed:', error);
        }
    }
    
    /**
     * Setup password strength indicator
     * @private
     */
    #setupPasswordStrengthIndicator() {
        try {
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            const strengthIndicator = document.querySelector(this.#fieldSelectors.passwordStrength);
            const suggestionsContainer = document.querySelector(this.#fieldSelectors.passwordSuggestions);
            
            if (passwordField && strengthIndicator) {
                passwordField.addEventListener('input', (event) => {
                    this.#updatePasswordStrength(event.target.value);
                });
                
                console.log('✅ Password strength indicator setup complete');
            }
            
        } catch (error) {
            console.error('❌ Password strength indicator setup failed:', error);
        }
    }
    
    /**
     * Setup auto-validation
     * @private
     */
    #setupAutoValidation() {
        try {
            // Validate on field blur
            const fields = ['username', 'email', 'firstName', 'lastName', 'password', 'confirmPassword'];
            
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
            // Update form data
            this.#formData[fieldName] = value;
            
            // Mark form as dirty
            this.#formState.isDirty = true;
            
            // Clear field error
            this.#clearFieldError(fieldName);
            
            // Special handling for password fields
            if (fieldName === 'password') {
                this.#updatePasswordStrength(value);
            } else if (fieldName === 'confirmPassword') {
                this.#validatePasswordMatch();
            }
            
            // Update form state
            this.#updateFormState();
            
        } catch (error) {
            console.error(`❌ Field input handling failed for ${fieldName}:`, error);
        }
    }
    
    /**
     * Update password strength
     * @private
     * @param {string} password - Password value
     */
    #updatePasswordStrength(password) {
        try {
            if (!password) {
                this.#passwordStrength = 0;
                this.#passwordSuggestions = [];
                this.#updatePasswordStrengthUI();
                return;
            }
            
            let strength = 0;
            const suggestions = [];
            
            // Length check
            if (password.length >= 8) strength++;
            else suggestions.push('Use at least 8 characters');
            
            // Uppercase check
            if (/[A-Z]/.test(password)) strength++;
            else suggestions.push('Include uppercase letters');
            
            // Lowercase check
            if (/[a-z]/.test(password)) strength++;
            else suggestions.push('Include lowercase letters');
            
            // Numbers check
            if (/\d/.test(password)) strength++;
            else suggestions.push('Include numbers');
            
            // Special characters check
            if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength++;
            else suggestions.push('Include special characters');
            
            // Update strength
            this.#passwordStrength = Math.min(strength, 4);
            this.#passwordSuggestions = suggestions;
            
            // Update UI
            this.#updatePasswordStrengthUI();
            
        } catch (error) {
            console.error('❌ Password strength update failed:', error);
        }
    }
    
    /**
     * Update password strength UI
     * @private
     */
    #updatePasswordStrengthUI() {
        try {
            const strengthIndicator = document.querySelector(this.#fieldSelectors.passwordStrength);
            const suggestionsContainer = document.querySelector(this.#fieldSelectors.passwordSuggestions);
            
            if (strengthIndicator) {
                const level = this.#passwordStrengthLevels[this.#passwordStrength];
                strengthIndicator.innerHTML = `
                    <div class="password-strength-bar">
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar ${level.class.replace('text-', 'bg-')}" 
                                 style="width: ${level.width}"></div>
                        </div>
                        <small class="${level.class} mt-1">${level.label}</small>
                    </div>
                `;
            }
            
            if (suggestionsContainer && this.#passwordSuggestions.length > 0) {
                suggestionsContainer.innerHTML = `
                    <div class="password-suggestions">
                        <small class="text-muted">Suggestions:</small>
                        <ul class="list-unstyled small mt-1">
                            ${this.#passwordSuggestions.map(suggestion => 
                                `<li class="text-muted">• ${suggestion}</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            } else if (suggestionsContainer) {
                suggestionsContainer.innerHTML = '';
            }
            
        } catch (error) {
            console.error('❌ Password strength UI update failed:', error);
        }
    }
    
    /**
     * Validate password match
     * @private
     */
    #validatePasswordMatch() {
        try {
            const password = this.#formData.password;
            const confirmPassword = this.#formData.confirmPassword;
            
            if (confirmPassword && password !== confirmPassword) {
                this.#showFieldError('confirmPassword', this.#errorMessages.confirmPassword.matchPassword);
            } else if (confirmPassword) {
                this.#clearFieldError('confirmPassword');
            }
            
        } catch (error) {
            console.error('❌ Password match validation failed:', error);
        }
    }
    
    /**
     * Validate a single field
     * @private
     * @param {string} fieldName - Field name
     * @param {string|boolean} value - Field value
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
            if (rules.required) {
                if (typeof value === 'boolean') {
                    if (!value) {
                        isValid = false;
                        errorMessage = this.#errorMessages[fieldName].required;
                    }
                } else if (!value || value.trim() === '') {
                    isValid = false;
                    errorMessage = this.#errorMessages[fieldName].required;
                }
            }
            
            // Length validation
            if (isValid && value && typeof value === 'string') {
                if (rules.minLength && value.length < rules.minLength) {
                    isValid = false;
                    errorMessage = this.#errorMessages[fieldName].minLength;
                } else if (rules.maxLength && value.length > rules.maxLength) {
                    isValid = false;
                    errorMessage = this.#errorMessages[fieldName].maxLength;
                }
            }
            
            // Pattern validation
            if (isValid && value && typeof value === 'string' && rules.pattern && !rules.pattern.test(value)) {
                isValid = false;
                errorMessage = this.#errorMessages[fieldName].pattern;
            }
            
            // Password strength validation
            if (isValid && fieldName === 'password' && value) {
                if (rules.requireUppercase && !/[A-Z]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.password.requireUppercase;
                } else if (rules.requireLowercase && !/[a-z]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.password.requireLowercase;
                } else if (rules.requireNumbers && !/\d/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.password.requireNumbers;
                } else if (rules.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.password.requireSpecialChars;
                }
            }
            
            // Password match validation
            if (isValid && fieldName === 'confirmPassword' && value) {
                if (value !== this.#formData.password) {
                    isValid = false;
                    errorMessage = this.#errorMessages.confirmPassword.matchPassword;
                }
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
            
            // Validate form
            if (!this.#validateAllFields()) {
                console.log('❌ Form validation failed');
                return;
            }
            
            // Set submitting state
            this.#setSubmittingState(true);
            
            // Attempt signup
            const success = await this.#attemptSignup();
            
            if (success) {
                this.#handleSignupSuccess();
            } else {
                this.#handleSignupFailure();
            }
            
        } catch (error) {
            console.error('❌ Form submission handling failed:', error);
            this.#handleSignupFailure();
        } finally {
            this.#setSubmittingState(false);
        }
    }
    
    /**
     * Attempt user signup
     * @private
     * @returns {Promise<boolean>} Signup success
     */
    async #attemptSignup() {
        try {
            console.log('📝 Attempting user signup...');
            
            // Prepare signup data
            const signupData = {
                username: this.#formData.username.trim(),
                email: this.#formData.email.trim().toLowerCase(),
                first_name: this.#formData.firstName.trim(),
                last_name: this.#formData.lastName.trim(),
                password: this.#formData.password
            };
            
            // Call signup API
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(signupData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Signup failed: ${response.status}`);
            }
            
            const signupResult = await response.json();
            
            console.log('✅ Signup successful');
            return true;
            
        } catch (error) {
            console.error('❌ Signup attempt failed:', error);
            return false;
        }
    }
    
    /**
     * Handle signup success
     * @private
     */
    #handleSignupSuccess() {
        try {
            // Show success message
            this.#showSuccessMessage('Account created successfully! You can now login.');
            
            // Reset form
            this.#resetForm();
            
            // Dispatch signup success event
            this.#dispatchSignupSuccess();
            
            // Switch to login tab after delay
            setTimeout(() => {
                this.#switchToLoginTab();
            }, 2000);
            
        } catch (error) {
            console.error('❌ Signup success handling failed:', error);
        }
    }
    
    /**
     * Handle signup failure
     * @private
     */
    #handleSignupFailure() {
        try {
            // Show error message
            this.#showGeneralError('Account creation failed. Please try again.');
            
            // Clear password fields
            const passwordField = document.querySelector(this.#fieldSelectors.password);
            const confirmPasswordField = document.querySelector(this.#fieldSelectors.confirmPassword);
            
            if (passwordField) {
                passwordField.value = '';
                this.#formData.password = '';
            }
            
            if (confirmPasswordField) {
                confirmPasswordField.value = '';
                this.#formData.confirmPassword = '';
            }
            
            // Reset password strength
            this.#passwordStrength = 0;
            this.#updatePasswordStrengthUI();
            
            // Focus username field
            const usernameField = document.querySelector(this.#fieldSelectors.username);
            if (usernameField) {
                usernameField.focus();
            }
            
            // Dispatch signup failure event
            this.#dispatchSignupFailure();
            
        } catch (error) {
            console.error('❌ Signup failure handling failed:', error);
        }
    }
    
    /**
     * Switch to login tab
     * @private
     */
    #switchToLoginTab() {
        try {
            // Find login tab and activate it
            const loginTab = document.querySelector('[data-bs-target="#login"]');
            if (loginTab) {
                const tab = new bootstrap.Tab(loginTab);
                tab.show();
            }
            
        } catch (error) {
            console.error('❌ Tab switch failed:', error);
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
                    ? '<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...'
                    : '<i class="fas fa-user-plus me-2"></i>Create Account';
            }
            
            // Disable form fields during submission
            const fields = ['username', 'email', 'firstName', 'lastName', 'password', 'confirmPassword', 'termsAccepted'];
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
                email: '',
                firstName: '',
                lastName: '',
                password: '',
                confirmPassword: '',
                termsAccepted: false
            };
            
            // Reset form fields
            const fields = ['username', 'email', 'firstName', 'lastName', 'password', 'confirmPassword'];
            fields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) field.value = '';
            });
            
            const termsField = document.querySelector(this.#fieldSelectors.termsAccepted);
            if (termsField) termsField.checked = false;
            
            // Clear errors
            this.#validationErrors = {};
            this.#clearAllFieldErrors();
            
            // Reset password strength
            this.#passwordStrength = 0;
            this.#updatePasswordStrengthUI();
            
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
     * Dispatch signup success event
     * @private
     */
    #dispatchSignupSuccess() {
        try {
            const event = new CustomEvent('signupSuccess', {
                detail: {
                    username: this.#formData.username,
                    email: this.#formData.email,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Signup success event dispatched');
            
        } catch (error) {
            console.error('❌ Signup success event dispatch failed:', error);
        }
    }
    
    /**
     * Dispatch signup failure event
     * @private
     */
    #dispatchSignupFailure() {
        try {
            const event = new CustomEvent('signupFailure', {
                detail: {
                    username: this.#formData.username,
                    email: this.#formData.email,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Signup failure event dispatched');
            
        } catch (error) {
            console.error('❌ Signup failure event dispatch failed:', error);
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
     * Get password strength
     * @readonly
     * @returns {number} Password strength (0-4)
     */
    get passwordStrength() {
        return this.#passwordStrength;
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
     * Get signup form status
     * @returns {Object} Form status
     */
    getSignupFormStatus() {
        return {
            isInitialized: this.#isInitialized,
            isSubmitting: this.#isSubmitting,
            formState: this.#formState,
            validationErrors: this.#validationErrors,
            passwordStrength: this.#passwordStrength
        };
    }
    
    /**
     * Create a default SignupForm instance
     * @static
     * @returns {SignupForm} New instance with default config
     */
    static createDefault() {
        return new SignupForm({
            formSelector: '#signupForm',
            autoValidate: true,
            showPasswordStrength: true,
            requireTerms: true,
            debug: false
        });
    }
}
