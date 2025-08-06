/**
 * Form Validation Component
 * Handles form validation and validation-related functionality
 */

export class FormValidator {
    constructor() {
        this.isInitialized = false;
        this.validatedForms = new Set();
    }

    /**
     * Initialize form validation
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('✅ Initializing Form Validator...');
        
        try {
            // Set up form validation
            this.setupFormValidation();
            
            // Set up real-time validation
            this.setupRealTimeValidation();
            
            this.isInitialized = true;
            console.log('✅ Form Validator initialized');
            
        } catch (error) {
            console.error('❌ Form Validator initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            if (!this.validatedForms.has(form)) {
                form.addEventListener('submit', (event) => {
                    this.handleFormSubmit(event);
                });
                
                this.validatedForms.add(form);
            }
        });
    }

    /**
     * Setup real-time validation
     */
    setupRealTimeValidation() {
        const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                this.clearFieldError(input);
            });
        });
    }

    /**
     * Handle form submission
     */
    handleFormSubmit(event) {
        const form = event.target;
        
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            
            // Show validation errors
            this.showFormErrors(form);
        } else {
            // Form is valid, proceed with submission
            this.hideFormErrors(form);
        }
        
        form.classList.add('was-validated');
    }

    /**
     * Validate individual field
     */
    validateField(input) {
        const value = input.value.trim();
        const fieldName = input.name;
        const fieldType = input.type;
        
        // Clear previous errors
        this.clearFieldError(input);
        
        // Required validation
        if (input.hasAttribute('required') && !value) {
            this.showFieldError(input, `${this.getFieldLabel(input)} is required`);
            return false;
        }
        
        // Type-specific validation
        if (value) {
            switch (fieldType) {
                case 'email':
                    if (!this.isValidEmail(value)) {
                        this.showFieldError(input, 'Please enter a valid email address');
                        return false;
                    }
                    break;
                    
                case 'url':
                    if (!this.isValidUrl(value)) {
                        this.showFieldError(input, 'Please enter a valid URL');
                        return false;
                    }
                    break;
                    
                case 'number':
                    if (!this.isValidNumber(value)) {
                        this.showFieldError(input, 'Please enter a valid number');
                        return false;
                    }
                    break;
                    
                case 'tel':
                    if (!this.isValidPhone(value)) {
                        this.showFieldError(input, 'Please enter a valid phone number');
                        return false;
                    }
                    break;
            }
            
            // Min/Max length validation
            if (input.hasAttribute('minlength')) {
                const minLength = parseInt(input.getAttribute('minlength'));
                if (value.length < minLength) {
                    this.showFieldError(input, `${this.getFieldLabel(input)} must be at least ${minLength} characters`);
                    return false;
                }
            }
            
            if (input.hasAttribute('maxlength')) {
                const maxLength = parseInt(input.getAttribute('maxlength'));
                if (value.length > maxLength) {
                    this.showFieldError(input, `${this.getFieldLabel(input)} must be no more than ${maxLength} characters`);
                    return false;
                }
            }
            
            // Pattern validation
            if (input.hasAttribute('pattern')) {
                const pattern = new RegExp(input.getAttribute('pattern'));
                if (!pattern.test(value)) {
                    this.showFieldError(input, `${this.getFieldLabel(input)} format is invalid`);
                    return false;
                }
            }
        }
        
        return true;
    }

    /**
     * Show field error
     */
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        // Find or create error message element
        let errorElement = input.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            input.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
    }

    /**
     * Clear field error
     */
    clearFieldError(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        const errorElement = input.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    /**
     * Show form errors
     */
    showFormErrors(form) {
        const invalidInputs = form.querySelectorAll('.is-invalid');
        if (invalidInputs.length > 0) {
            // Focus on first invalid input
            invalidInputs[0].focus();
        }
    }

    /**
     * Hide form errors
     */
    hideFormErrors(form) {
        const inputs = form.querySelectorAll('.is-invalid');
        inputs.forEach(input => {
            this.clearFieldError(input);
        });
    }

    /**
     * Get field label
     */
    getFieldLabel(input) {
        const label = input.parentNode.querySelector('label');
        return label ? label.textContent.replace('*', '').trim() : input.name;
    }

    /**
     * Validation helper methods
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    isValidNumber(value) {
        return !isNaN(value) && !isNaN(parseFloat(value));
    }

    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }

    /**
     * Validate entire form
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Reset form validation
     */
    resetFormValidation(form) {
        const inputs = form.querySelectorAll('.is-invalid, .is-valid');
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });
        
        form.classList.remove('was-validated');
    }

    /**
     * Cleanup form validator
     */
    destroy() {
        this.validatedForms.clear();
        this.isInitialized = false;
        console.log('🧹 Form Validator destroyed');
    }
} 