/**
 * Signup Form UI Component
 * Handles signup form interactions and validation
 * CACHE BUST: 2025-08-10-20:07
 */

export default class SignupForm {
    constructor() {
        this.form = null;
        this.submitButton = null;
        this.loadingSpinner = null;
        this.alertContainer = null;
        this.isSubmitting = false;
    }

    /**
     * Initialize signup form
     */
    init() {
        console.log('📝 Initializing Signup Form...');
        
        this.form = document.getElementById('signupForm');
        this.submitButton = document.getElementById('signupBtn');
        this.loadingSpinner = document.getElementById('signupLoadingSpinner');
        this.alertContainer = document.getElementById('signup-alert-container');
        
        if (this.form) {
            this.setupEventListeners();
            console.log('✅ Signup Form initialized');
        } else {
            console.warn('⚠️ Signup form not found');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Password visibility toggles
        const passwordToggle = document.getElementById('passwordToggle');
        const confirmPasswordToggle = document.getElementById('confirmPasswordToggle');
        
        if (passwordToggle) {
            passwordToggle.addEventListener('click', () => this.togglePasswordVisibility('password'));
        }
        
        if (confirmPasswordToggle) {
            confirmPasswordToggle.addEventListener('click', () => this.togglePasswordVisibility('confirmPassword'));
        }
        
        // Real-time validation
        const usernameInput = document.getElementById('signup_username');
        const emailInput = document.getElementById('signup_email');
        const passwordInput = document.getElementById('signup_password');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        
        if (usernameInput) {
            usernameInput.addEventListener('input', () => this.validateUsername());
        }
        
        if (emailInput) {
            emailInput.addEventListener('input', () => this.validateEmail());
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                this.validatePassword();
                this.validatePasswordMatch();
            });
        }
        
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', () => this.validatePasswordMatch());
        }
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        
        // Validate form
        if (!this.validateForm()) {
            return;
        }
        
        this.setSubmittingState(true);
        this.clearAlerts();
        
        try {
            const formData = new FormData();
            formData.append('username', document.getElementById('signup_username').value.trim());
            formData.append('email', document.getElementById('signup_email').value.trim());
            formData.append('password', document.getElementById('password').value);
            formData.append('confirm_password', document.getElementById('confirmPassword').value);
            formData.append('full_name', document.getElementById('fullName')?.value.trim() || '');
            
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccess(result.message || 'Registration successful! Please check your email to verify your account.');
                
                // Reset form
                setTimeout(() => {
                    this.reset();
                }, 2000);
            } else {
                this.showError(result.error || 'Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Signup error:', error);
            this.showError('Registration failed. Please check your connection and try again.');
        } finally {
            this.setSubmittingState(false);
        }
    }

    /**
     * Validate form
     */
    validateForm() {
        const username = document.getElementById('signup_username').value.trim();
        const email = document.getElementById('signup_email').value.trim();
        const password = document.getElementById('signup_password').value;
        const confirmPassword = document.getElementById('signup_confirm_password').value;
        
        let isValid = true;
        
        if (!username) {
            this.showFieldError('username', 'Username is required');
            isValid = false;
        }
        
        if (!email) {
            this.showFieldError('email', 'Email is required');
            isValid = false;
        }
        
        if (!password) {
            this.showFieldError('password', 'Password is required');
            isValid = false;
        }
        
        if (!confirmPassword) {
            this.showFieldError('confirmPassword', 'Please confirm your password');
            isValid = false;
        }
        
        return isValid;
    }

    /**
     * Validate username
     */
    validateUsername() {
        const username = document.getElementById('signup_username').value.trim();
        
        if (!username) {
            this.showFieldError('username', 'Username is required');
            return false;
        }
        
        if (username.length < 3) {
            this.showFieldError('username', 'Username must be at least 3 characters');
            return false;
        }
        
        if (username.length > 20) {
            this.showFieldError('username', 'Username must be less than 20 characters');
            return false;
        }
        
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            this.showFieldError('username', 'Username can only contain letters, numbers, and underscores');
            return false;
        }
        
        this.clearFieldError('username');
        return true;
    }

    /**
     * Validate email
     */
    validateEmail() {
        const email = document.getElementById('email').value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            this.showFieldError('email', 'Email is required');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            this.showFieldError('email', 'Please enter a valid email address');
            return false;
        }
        
        this.clearFieldError('email');
        return true;
    }

    /**
     * Validate password
     */
    validatePassword() {
        const password = document.getElementById('password').value;
        const strengthIndicator = document.getElementById('passwordStrength');
        
        if (!password) {
            this.showFieldError('password', 'Password is required');
            return false;
        }
        
        if (password.length < 8) {
            this.showFieldError('password', 'Password must be at least 8 characters');
            return false;
        }
        
        // Check password strength
        let strength = 0;
        let feedback = '';
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        switch (strength) {
            case 0:
            case 1:
                feedback = '<span class="strength-weak">Very Weak</span>';
                break;
            case 2:
                feedback = '<span class="strength-weak">Weak</span>';
                break;
            case 3:
                feedback = '<span class="strength-medium">Medium</span>';
                break;
            case 4:
                feedback = '<span class="strength-strong">Strong</span>';
                break;
            case 5:
                feedback = '<span class="strength-strong">Very Strong</span>';
                break;
        }
        
        if (strengthIndicator) {
            strengthIndicator.innerHTML = `Password strength: ${feedback}`;
        }
        
        this.clearFieldError('password');
        return true;
    }

    /**
     * Validate password match
     */
    validatePasswordMatch() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (!confirmPassword) {
            this.showFieldError('confirmPassword', 'Please confirm your password');
            return false;
        }
        
        if (password !== confirmPassword) {
            this.showFieldError('confirmPassword', 'Passwords do not match');
            return false;
        }
        
        this.clearFieldError('confirmPassword');
        return true;
    }

    /**
     * Show field error
     */
    showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        const errorDiv = document.getElementById(`${fieldName}Error`);
        
        if (field) {
            field.classList.add('is-invalid');
        }
        
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    /**
     * Clear field error
     */
    clearFieldError(fieldName) {
        const field = document.getElementById(fieldName);
        const errorDiv = document.getElementById(`${fieldName}Error`);
        
        if (field) {
            field.classList.remove('is-invalid');
        }
        
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    /**
     * Toggle password visibility
     */
    togglePasswordVisibility(fieldName) {
        const passwordInput = document.getElementById(fieldName);
        const toggleButton = document.getElementById(`${fieldName}Toggle`);
        const icon = toggleButton.querySelector('i');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.className = 'fas fa-eye-slash';
        } else {
            passwordInput.type = 'password';
            icon.className = 'fas fa-eye';
        }
    }

    /**
     * Set submitting state
     */
    setSubmittingState(submitting) {
        this.isSubmitting = submitting;
        
        if (this.submitButton) {
            this.submitButton.disabled = submitting;
        }
        
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = submitting ? 'inline-block' : 'none';
        }
        
        const submitText = document.getElementById('signupText');
        if (submitText) {
            submitText.textContent = submitting ? 'Creating Account...' : 'Sign Up';
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (this.alertContainer) {
            this.alertContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> ${message}
                </div>
            `;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.alertContainer) {
            this.alertContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> ${message}
                </div>
            `;
        }
    }

    /**
     * Clear alerts
     */
    clearAlerts() {
        if (this.alertContainer) {
            this.alertContainer.innerHTML = '';
        }
    }

    /**
     * Reset form
     */
    reset() {
        if (this.form) {
            this.form.reset();
        }
        this.clearAlerts();
        this.clearFieldError('username');
        this.clearFieldError('email');
        this.clearFieldError('password');
        this.clearFieldError('confirmPassword');
        
        const strengthIndicator = document.getElementById('passwordStrength');
        if (strengthIndicator) {
            strengthIndicator.textContent = '';
        }
    }

    /**
     * Destroy component
     */
    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit);
        }
    }
} 