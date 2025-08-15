/**
 * Profile Form - User Profile Management Interface
 * @description Handles user profile editing and password changes with validation
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-forms/profile-form
 */

export default class ProfileForm {
    // Private fields
    #isInitialized = false;
    #form = null;
    #formData = {};
    #validationErrors = {};
    #isSubmitting = false;
    #passwordStrength = 0;
    #currentUser = null;
    #config = {};
    #fieldSelectors = {};
    #formState = {};
    #validationRules = {};
    #errorMessages = {};
    #formStateUpdateTimeout = null;
    #handleFieldInputBound = null;
    #handleFieldBlurBound = null;
    #formStateUpdateCount = 0;
    #maxFormStateUpdates = 1000; // Safety limit
    
    constructor(options = {}) {
        // Configuration
        this.#config = {
            formSelector: options.formSelector ?? '#profileForm',
            autoValidate: options.autoValidate ?? true,
            showPasswordStrength: options.showPasswordStrength ?? true,
            debug: options.debug ?? false
        };
        
        // Form field selectors
        this.#fieldSelectors = {
            // Profile fields
            fullName: '#full_name',
            email: '#email',
            phone: '#phone',
            organizationId: '#organization_id',
            jobTitle: '#job_title',
            department: '#department',
            bio: '#bio',
            
            // Password change fields
            currentPassword: '#currentPassword',
            newPassword: '#newPassword',
            confirmPassword: '#confirmNewPassword',
            
            // Form controls
            submitButton: '#profileSubmit',
            passwordSubmitButton: '#passwordSubmit',
            errorContainer: '#profileErrors',
            successContainer: '#profileSuccess',
            passwordStrength: '#passwordStrength'
        };
        
        // Form state
        this.#formState = {
            isValid: false,
            isDirty: false,
            hasErrors: false,
            lastValidation: null,
            isUpdating: false,
            isInitializing: false,
            updateRetryCount: 0,
            maxUpdateRetries: 3
        };
        
        // Validation rules
        this.#validationRules = {
            fullName: {
                required: true,
                minLength: 2,
                maxLength: 100,
                pattern: /^[a-zA-Z\s'-]+$/
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            },
            phone: {
                required: false,
                pattern: /^[\+]?[1-9][\d]{0,15}$/
            },
            organizationId: {
                required: false
            },
            jobTitle: {
                required: false,
                maxLength: 100
            },
            department: {
                required: false,
                maxLength: 100
            },
            bio: {
                required: false,
                maxLength: 500
            },
            currentPassword: {
                required: true
            },
            newPassword: {
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
            }
        };
        
        // Error messages
        this.#errorMessages = {
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
            email: {
                required: 'Email is required',
                pattern: 'Please enter a valid email address'
            },
            phone: {
                pattern: 'Please enter a valid phone number'
            },
            organization: {
                maxLength: 'Organization name must be less than 100 characters'
            },
            currentPassword: {
                required: 'Current password is required'
            },
            newPassword: {
                required: 'New password is required',
                minLength: 'Password must be at least 8 characters',
                maxLength: 'Password must be less than 128 characters',
                requireUppercase: 'Password must contain at least one uppercase letter',
                requireLowercase: 'Password must contain at least one lowercase letter',
                requireNumbers: 'Password must contain at least one number',
                requireSpecialChars: 'Password must contain at least one special character'
            },
            confirmPassword: {
                required: 'Please confirm your new password',
                matchPassword: 'Passwords do not match'
            }
        };
        
        // Create bound event handlers to prevent duplicate listeners
        this.#handleFieldInputBound = this.#handleFieldInput.bind(this);
        this.#handleFieldBlurBound = this.#handleFieldBlur.bind(this);
        
        console.log('👤 ProfileForm created with config:', this.#config);
    }
    
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ ProfileForm already initialized');
                return true;
            }
            
            // Safety check: prevent concurrent initialization
            if (this.#formState.isInitializing) {
                console.log('⚠️ ProfileForm initialization already in progress');
                return false;
            }
            
            this.#formState.isInitializing = true;
            console.log('👤 Initializing ProfileForm...');
            
            // Find the form element
            await this.#findFormElement();
            
            // Load current user data
            await this.#loadCurrentUser();
            
            // Setup form fields
            this.#setupFormFields();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            // Setup password strength indicator
            if (this.#config.showPasswordStrength) {
                this.#setupPasswordStrengthIndicator();
            }
            
            // Initial form state (use immediate update for initialization)
            this.#updateFormState();
            
            this.#isInitialized = true;
            this.#formState.isInitializing = false;
            console.log('✅ ProfileForm initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ ProfileForm initialization failed:', error);
            this.#formState.isInitializing = false;
            throw error;
        }
    }
    
    async #findFormElement() {
        try {
            this.#form = document.querySelector(this.#config.formSelector);
            
            if (!this.#form) {
                throw new Error(`Profile form not found with selector: ${this.#config.formSelector}`);
            }
            
            console.log('✅ Profile form element found');
            
        } catch (error) {
            console.error('❌ Form element discovery failed:', error);
            throw error;
        }
    }
    
    async #loadCurrentUser() {
        try {
            // Get user data from storage
            const userData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
            const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
            
            if (userData && token) {
                this.#currentUser = JSON.parse(userData);
                console.log('✅ Current user data loaded from storage');
            } else if (token) {
                // Only try API if we have a token
                const response = await fetch('/api/auth/profile', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    this.#currentUser = await response.json();
                    console.log('✅ Current user data loaded from API');
                } else {
                    console.log('⚠️ User not authenticated yet, profile form will be populated when user logs in');
                    this.#currentUser = null;
                }
            } else {
                console.log('⚠️ No authentication token found, profile form will be populated when user logs in');
                this.#currentUser = null;
            }
            
        } catch (error) {
            console.log('⚠️ User data loading failed (this is normal for unauthenticated users):', error.message);
            this.#currentUser = null;
        }
    }
    
    #setupFormFields() {
        try {
            // Initialize form data with current user data
            this.#formData = {
                firstName: this.#currentUser?.first_name || '',
                lastName: this.#currentUser?.last_name || '',
                email: this.#currentUser?.email || '',
                phone: this.#currentUser?.phone || '',
                organization: this.#currentUser?.organization || '',
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            };
            
            // Populate form fields
            this.#populateFormFields();
            
            console.log('✅ Form fields setup complete');
            
        } catch (error) {
            console.error('❌ Form fields setup failed:', error);
        }
    }
    
    #populateFormFields() {
        try {
            // Profile fields
            const firstNameField = document.querySelector(this.#fieldSelectors.firstName);
            const lastNameField = document.querySelector(this.#fieldSelectors.lastName);
            const emailField = document.querySelector(this.#fieldSelectors.email);
            const phoneField = document.querySelector(this.#fieldSelectors.phone);
            const organizationField = document.querySelector(this.#fieldSelectors.organization);
            
            if (firstNameField) firstNameField.value = this.#formData.firstName;
            if (lastNameField) lastNameField.value = this.#formData.lastName;
            if (emailField) emailField.value = this.#formData.email;
            if (phoneField) phoneField.value = this.#formData.phone;
            if (organizationField) organizationField.value = this.#formData.organization;
            
        } catch (error) {
            console.error('❌ Form field population failed:', error);
        }
    }
    
    #setupEventListeners() {
        try {
            // Profile form submission
            const profileForm = document.querySelector('#profileForm');
            if (profileForm) {
                profileForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    this.#handleProfileSubmit();
                });
            }
            
            // Password form submission
            const passwordForm = document.querySelector('#passwordForm');
            if (passwordForm) {
                passwordForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    this.#handlePasswordSubmit();
                });
            }
            
            // Field input events (consolidated to prevent duplicates)
            const profileFields = ['firstName', 'lastName', 'email', 'phone', 'organization'];
            profileFields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    // Remove any existing listeners to prevent duplicates
                    field.removeEventListener('input', this.#handleFieldInputBound);
                    field.removeEventListener('blur', this.#handleFieldBlurBound);
                    
                    // Add new listeners with field name context
                    field.addEventListener('input', (event) => {
                        this.#handleFieldInput(fieldName, event.target.value);
                    });
                    field.addEventListener('blur', (event) => {
                        this.#handleFieldBlur(fieldName, event.target.value);
                    });
                }
            });
            
            // Password field events (consolidated to prevent duplicates)
            const passwordFields = ['currentPassword', 'newPassword', 'confirmPassword'];
            passwordFields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    // Remove any existing listeners to prevent duplicates
                    field.removeEventListener('input', this.#handleFieldInputBound);
                    field.removeEventListener('blur', this.#handleFieldBlurBound);
                    
                    // Add new listeners with field name context
                    field.addEventListener('input', (event) => {
                        this.#handleFieldInput(fieldName, event.target.value);
                    });
                    field.addEventListener('blur', (event) => {
                        this.#handleFieldBlur(fieldName, event.target.value);
                    });
                }
            });
            
            console.log('👂 Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listeners setup failed:', error);
        }
    }
    
    #setupPasswordStrengthIndicator() {
        try {
            // Password strength indicator is now handled in the main event listeners
            // This method is kept for compatibility but no longer adds duplicate listeners
            console.log('✅ Password strength indicator setup complete (handled by main listeners)');
            
        } catch (error) {
            console.error('❌ Password strength indicator setup failed:', error);
        }
    }
    
    #handleFieldInput(fieldName, value) {
        try {
            // Update form data
            this.#formData[fieldName] = value;
            
            // Mark form as dirty
            this.#formState.isDirty = true;
            
            // Clear field error
            this.#clearFieldError(fieldName);
            
            // Special handling for password fields
            if (fieldName === 'newPassword') {
                this.#updatePasswordStrength(value);
            } else if (fieldName === 'confirmPassword') {
                this.#validatePasswordMatch();
            }
            
            // Update form state (debounced to prevent excessive updates)
            this.#debouncedUpdateFormState();
            
        } catch (error) {
            console.error(`❌ Field input handling failed for ${fieldName}:`, error);
        }
    }
    
    #handleFieldBlur(fieldName, value) {
        try {
            // Validate field on blur
            this.#validateField(fieldName, value);
        } catch (error) {
            console.error(`❌ Field blur handling failed for ${fieldName}:`, error);
        }
    }
    
    #updatePasswordStrength(password) {
        try {
            if (!password) {
                this.#passwordStrength = 0;
                this.#updatePasswordStrengthUI();
                return;
            }
            
            let strength = 0;
            
            // Length check
            if (password.length >= 8) strength++;
            
            // Uppercase check
            if (/[A-Z]/.test(password)) strength++;
            
            // Lowercase check
            if (/[a-z]/.test(password)) strength++;
            
            // Numbers check
            if (/\d/.test(password)) strength++;
            
            // Special characters check
            if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength++;
            
            // Update strength
            this.#passwordStrength = Math.min(strength, 4);
            
            // Update UI
            this.#updatePasswordStrengthUI();
            
        } catch (error) {
            console.error('❌ Password strength update failed:', error);
        }
    }
    
    #updatePasswordStrengthUI() {
        try {
            const strengthIndicator = document.querySelector(this.#fieldSelectors.passwordStrength);
            
            if (strengthIndicator) {
                const levels = {
                    0: { label: 'Very Weak', class: 'text-danger', width: '20%' },
                    1: { label: 'Weak', class: 'text-warning', width: '40%' },
                    2: { label: 'Fair', class: 'text-warning', width: '60%' },
                    3: { label: 'Good', class: 'text-info', width: '80%' },
                    4: { label: 'Strong', class: 'text-success', width: '100%' }
                };
                
                const level = levels[this.#passwordStrength];
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
            
        } catch (error) {
            console.error('❌ Password strength UI update failed:', error);
        }
    }
    
    #validatePasswordMatch() {
        try {
            const newPassword = this.#formData.newPassword;
            const confirmPassword = this.#formData.confirmPassword;
            
            if (confirmPassword && newPassword !== confirmPassword) {
                this.#showFieldError('confirmPassword', this.#errorMessages.confirmPassword.matchPassword);
            } else if (confirmPassword) {
                this.#clearFieldError('confirmPassword');
            }
            
        } catch (error) {
            console.error('❌ Password match validation failed:', error);
        }
    }
    
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
            if (isValid && fieldName === 'newPassword' && value) {
                if (rules.requireUppercase && !/[A-Z]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.newPassword.requireUppercase;
                } else if (rules.requireLowercase && !/[a-z]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.newPassword.requireLowercase;
                } else if (rules.requireNumbers && !/\d/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.newPassword.requireNumbers;
                } else if (rules.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)) {
                    isValid = false;
                    errorMessage = this.#errorMessages.newPassword.requireSpecialChars;
                }
            }
            
            // Password match validation
            if (isValid && fieldName === 'confirmPassword' && value) {
                if (value !== this.#formData.newPassword) {
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
            
            return isValid;
            
        } catch (error) {
            console.error(`❌ Field validation failed for ${fieldName}:`, error);
            return false;
        }
    }
    
    #validateProfileFields() {
        try {
            let isValid = true;
            const profileFields = ['firstName', 'lastName', 'email', 'phone', 'organization'];
            
            for (const fieldName of profileFields) {
                const value = this.#formData[fieldName];
                if (!this.#validateField(fieldName, value)) {
                    isValid = false;
                }
            }
            
            return isValid;
            
        } catch (error) {
            console.error('❌ Profile fields validation failed:', error);
            return false;
        }
    }
    
    #validatePasswordFields() {
        try {
            let isValid = true;
            const passwordFields = ['currentPassword', 'newPassword', 'confirmPassword'];
            
            for (const fieldName of passwordFields) {
                const value = this.#formData[fieldName];
                if (!this.#validateField(fieldName, value)) {
                    isValid = false;
                }
            }
            
            return isValid;
            
        } catch (error) {
            console.error('❌ Password fields validation failed:', error);
            return false;
        }
    }
    
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
    
    async #handleProfileSubmit() {
        try {
            if (this.#isSubmitting) {
                console.log('⚠️ Profile submission already in progress');
                return;
            }
            
            // Validate profile fields
            if (!this.#validateProfileFields()) {
                console.log('❌ Profile validation failed');
                return;
            }
            
            // Set submitting state
            this.#setSubmittingState(true, 'profile');
            
            // Attempt profile update
            const success = await this.#updateProfile();
            
            if (success) {
                this.#handleProfileSuccess();
            } else {
                this.#handleProfileFailure();
            }
            
        } catch (error) {
            console.error('❌ Profile submission handling failed:', error);
            this.#handleProfileFailure();
        } finally {
            this.#setSubmittingState(false, 'profile');
        }
    }
    
    async #handlePasswordSubmit() {
        try {
            if (this.#isSubmitting) {
                console.log('⚠️ Password submission already in progress');
                return;
            }
            
            // Validate password fields
            if (!this.#validatePasswordFields()) {
                console.log('❌ Password validation failed');
                return;
            }
            
            // Set submitting state
            this.#setSubmittingState(true, 'password');
            
            // Attempt password change
            const success = await this.#changePassword();
            
            if (success) {
                this.#handlePasswordSuccess();
            } else {
                this.#handlePasswordFailure();
            }
            
        } catch (error) {
            console.error('❌ Password submission handling failed:', error);
            this.#handlePasswordFailure();
        } finally {
            this.#setSubmittingState(false, 'password');
        }
    }
    
    async #updateProfile() {
        try {
            console.log('👤 Updating user profile...');
            
            // Prepare profile data
            const profileData = {
                first_name: this.#formData.firstName.trim(),
                last_name: this.#formData.lastName.trim(),
                email: this.#formData.email.trim().toLowerCase(),
                phone: this.#formData.phone.trim() || null,
                organization: this.#formData.organization.trim() || null
            };
            
            // Call profile update API
            const response = await fetch('/api/auth/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(profileData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Profile update failed: ${response.status}`);
            }
            
            const updatedProfile = await response.json();
            
            // Update current user data
            this.#currentUser = { ...this.#currentUser, ...updatedProfile };
            
            // Update storage
            const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage;
            storage.setItem('user_data', JSON.stringify(this.#currentUser));
            
            console.log('✅ Profile update successful');
            return true;
            
        } catch (error) {
            console.error('❌ Profile update failed:', error);
            return false;
        }
    }
    
    async #changePassword() {
        try {
            console.log('🔐 Changing user password...');
            
            // Prepare password data
            const passwordData = {
                current_password: this.#formData.currentPassword,
                new_password: this.#formData.newPassword
            };
            
            // Call password change API
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(passwordData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Password change failed: ${response.status}`);
            }
            
            console.log('✅ Password change successful');
            return true;
            
        } catch (error) {
            console.error('❌ Password change failed:', error);
            return false;
        }
    }
    
    #handleProfileSuccess() {
        try {
            // Show success message
            this.#showSuccessMessage('Profile updated successfully!');
            
            // Clear password fields
            this.#clearPasswordFields();
            
            // Dispatch profile update event
            this.#dispatchProfileUpdated();
            
        } catch (error) {
            console.error('❌ Profile success handling failed:', error);
        }
    }
    
    #handleProfileFailure() {
        try {
            // Show error message
            this.#showGeneralError('Profile update failed. Please try again.');
            
            // Dispatch profile update failure event
            this.#dispatchProfileUpdateFailure();
            
        } catch (error) {
            console.error('❌ Profile failure handling failed:', error);
        }
    }
    
    #handlePasswordSuccess() {
        try {
            // Show success message
            this.#showSuccessMessage('Password changed successfully!');
            
            // Clear password fields
            this.#clearPasswordFields();
            
            // Dispatch password change event
            this.#dispatchPasswordChanged();
            
        } catch (error) {
            console.error('❌ Password success handling failed:', error);
        }
    }
    
    #handlePasswordFailure() {
        try {
            // Show error message
            this.#showGeneralError('Password change failed. Please check your current password.');
            
            // Clear current password field
            const currentPasswordField = document.querySelector(this.#fieldSelectors.currentPassword);
            if (currentPasswordField) {
                currentPasswordField.value = '';
                this.#formData.currentPassword = '';
            }
            
            // Focus current password field
            if (currentPasswordField) {
                currentPasswordField.focus();
            }
            
            // Dispatch password change failure event
            this.#dispatchPasswordChangeFailure();
            
        } catch (error) {
            console.error('❌ Password failure handling failed:', error);
        }
    }
    
    #clearPasswordFields() {
        try {
            const passwordFields = ['currentPassword', 'newPassword', 'confirmPassword'];
            passwordFields.forEach(fieldName => {
                const field = document.querySelector(this.#fieldSelectors[fieldName]);
                if (field) {
                    field.value = '';
                    this.#formData[fieldName] = '';
                }
            });
            
            // Reset password strength
            this.#passwordStrength = 0;
            this.#updatePasswordStrengthUI();
            
            // Clear password errors
            passwordFields.forEach(fieldName => {
                this.#clearFieldError(fieldName);
            });
            
        } catch (error) {
            console.error('❌ Password fields clear failed:', error);
        }
    }
    
    #setSubmittingState(isSubmitting, formType) {
        try {
            this.#isSubmitting = isSubmitting;
            
            if (formType === 'profile') {
                const submitButton = document.querySelector(this.#fieldSelectors.submitButton);
                if (submitButton) {
                    submitButton.disabled = isSubmitting;
                    submitButton.innerHTML = isSubmitting 
                        ? '<i class="fas fa-spinner fa-spin me-2"></i>Updating Profile...'
                        : '<i class="fas fa-save me-2"></i>Update Profile';
                }
                
                // Disable profile fields during submission
                const profileFields = ['firstName', 'lastName', 'email', 'phone', 'organization'];
                profileFields.forEach(fieldName => {
                    const field = document.querySelector(this.#fieldSelectors[fieldName]);
                    if (field) {
                        field.disabled = isSubmitting;
                    }
                });
                
            } else if (formType === 'password') {
                const passwordSubmitButton = document.querySelector(this.#fieldSelectors.passwordSubmitButton);
                if (passwordSubmitButton) {
                    passwordSubmitButton.disabled = isSubmitting;
                    passwordSubmitButton.innerHTML = isSubmitting 
                        ? '<i class="fas fa-spinner fa-spin me-2"></i>Changing Password...'
                        : '<i class="fas fa-key me-2"></i>Change Password';
                }
                
                // Disable password fields during submission
                const passwordFields = ['currentPassword', 'newPassword', 'confirmPassword'];
                passwordFields.forEach(fieldName => {
                    const field = document.querySelector(this.#fieldSelectors[fieldName]);
                    if (field) {
                        field.disabled = isSubmitting;
                    }
                });
            }
            
        } catch (error) {
            console.error('❌ Submitting state update failed:', error);
        }
    }
    
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
    
    #updateFormState() {
        try {
            // Safety check: prevent infinite loops
            if (this.#formState.isUpdating) {
                console.log('⚠️ Form state update already in progress, skipping');
                return;
            }
            
            // Safety check: prevent excessive retries
            if (this.#formState.updateRetryCount >= this.#formState.maxUpdateRetries) {
                console.warn('⚠️ Maximum form state update retries reached, skipping update');
                return;
            }
            
            // Set updating flag
            this.#formState.isUpdating = true;
            
            // Increment retry counter
            this.#formState.updateRetryCount++;
            
            // Safety timeout: automatically clear updating flag after 5 seconds
            setTimeout(() => {
                if (this.#formState.isUpdating) {
                    console.warn('⚠️ Form state update timeout reached, clearing updating flag');
                    this.#formState.isUpdating = false;
                    this.#formState.updateRetryCount = 0;
                }
            }, 5000);
            
            // Check if form is valid
            this.#formState.isValid = Object.keys(this.#validationErrors).length === 0;
            
            // Check if form has errors
            this.#formState.hasErrors = Object.keys(this.#validationErrors).length > 0;
            
            // Update last validation timestamp
            this.#formState.lastValidation = Date.now();
            
            // Update submit buttons state based on current validation state
            const profileSubmitButton = document.querySelector(this.#fieldSelectors.submitButton);
            const passwordSubmitButton = document.querySelector(this.#fieldSelectors.passwordSubmitButton);
            
            if (profileSubmitButton) {
                // Check if profile fields have values and no errors
                const profileFields = ['firstName', 'lastName', 'email'];
                const hasProfileValues = profileFields.every(field => 
                    this.#formData[field] && this.#formData[field].trim() !== ''
                );
                const hasProfileErrors = profileFields.some(field => 
                    this.#validationErrors[field]
                );
                profileSubmitButton.disabled = !hasProfileValues || hasProfileErrors || this.#isSubmitting;
            }
            
            if (passwordSubmitButton) {
                // Check if password fields have values and no errors
                const passwordFields = ['currentPassword', 'newPassword', 'confirmPassword'];
                const hasPasswordValues = passwordFields.every(field => 
                    this.#formData[field] && this.#formData[field].trim() !== ''
                );
                const hasPasswordErrors = passwordFields.every(field => 
                    this.#validationErrors[field]
                );
                passwordSubmitButton.disabled = !hasPasswordValues || hasPasswordErrors || this.#isSubmitting;
            }
            
        } catch (error) {
            console.error('❌ Form state update failed:', error);
        } finally {
            // Clear updating flag
            this.#formState.isUpdating = false;
            
            // Reset retry counter on successful update
            this.#formState.updateRetryCount = 0;
        }
    }
    
    #debouncedUpdateFormState() {
        try {
            // Safety check: prevent excessive updates
            if (this.#formState.isUpdating) {
                return;
            }
            
            // Safety check: prevent too many queued updates
            if (this.#formStateUpdateTimeout && this.#formState.updateRetryCount > 0) {
                console.log('⚠️ Skipping debounced update due to recent retries');
                return;
            }
            
            // Clear existing timeout
            if (this.#formStateUpdateTimeout) {
                clearTimeout(this.#formStateUpdateTimeout);
            }
            
            // Set new timeout for debounced update
            this.#formStateUpdateTimeout = setTimeout(() => {
                this.#updateFormState();
            }, 100); // 100ms debounce
        } catch (error) {
            console.error('❌ Debounced form state update failed:', error);
        }
    }
    
    #dispatchProfileUpdated() {
        try {
            const event = new CustomEvent('profileUpdated', {
                detail: {
                    user: this.#currentUser,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Profile updated event dispatched');
            
        } catch (error) {
            console.error('❌ Profile updated event dispatch failed:', error);
        }
    }
    
    #dispatchProfileUpdateFailure() {
        try {
            const event = new CustomEvent('profileUpdateFailure', {
                detail: {
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Profile update failure event dispatched');
            
        } catch (error) {
            console.error('❌ Profile update failure event dispatch failed:', error);
        }
    }
    
    #dispatchPasswordChanged() {
        try {
            const event = new CustomEvent('passwordChanged', {
                detail: {
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Password changed event dispatched');
            
        } catch (error) {
            console.error('❌ Password changed event dispatch failed:', error);
        }
    }
    
    #dispatchPasswordChangeFailure() {
        try {
            const event = new CustomEvent('passwordChangeFailure', {
                detail: {
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 Password change failure event dispatched');
            
        } catch (error) {
            console.error('❌ Password change failure event dispatch failed:', error);
        }
    }
    
    // Getters
    get formData() { return { ...this.#formData }; }
    get formState() { return { ...this.#formState }; }
    get validationErrors() { return { ...this.#validationErrors }; }
    get passwordStrength() { return this.#passwordStrength; }
    get isSubmitting() { return this.#isSubmitting; }
    get isInitialized() { return this.#isInitialized; }
    get currentUser() { return { ...this.#currentUser }; }
    
    getProfileFormStatus() {
        return {
            isInitialized: this.#isInitialized,
            isSubmitting: this.#isSubmitting,
            formState: this.#formState,
            validationErrors: this.#validationErrors,
            passwordStrength: this.#passwordStrength,
            hasCurrentUser: !!this.#currentUser
        };
    }
    
    static createDefault() {
        return new ProfileForm({
            formSelector: '#profileForm',
            autoValidate: true,
            showPasswordStrength: true,
            debug: false
        });
    }
}
