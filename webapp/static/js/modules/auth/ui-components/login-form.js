/**
 * Login Form UI Component
 * Handles login form interactions and validation
 */

export default class LoginForm {
    constructor() {
        this.form = null;
        this.submitButton = null;
        this.loadingSpinner = null;
        this.alertContainer = null;
        this.isSubmitting = false;
    }

    /**
     * Initialize login form
     */
    init() {
        console.log('🔐 Initializing Login Form...');
        
        this.form = document.getElementById('loginForm');
        this.submitButton = document.getElementById('loginBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.alertContainer = document.getElementById('alert-container');
        
        if (this.form) {
            this.setupEventListeners();
            console.log('✅ Login Form initialized');
        } else {
            console.warn('⚠️ Login form not found');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Password visibility toggle
        const passwordToggle = document.getElementById('passwordToggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', () => this.togglePasswordVisibility());
        }
        
        // Real-time validation
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');
        
        if (usernameInput) {
            usernameInput.addEventListener('input', () => this.validateUsername());
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('input', () => this.validatePassword());
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
            formData.append('username', document.getElementById('username').value);
            formData.append('password', document.getElementById('password').value);
            formData.append('remember_me', document.getElementById('rememberMe')?.checked || false);
            
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccess(result.message || 'Login successful!');
                
                // Check for password expiration warnings
                if (result.password_expiration) {
                    const expiration = result.password_expiration;
                    if (expiration.expired) {
                        this.showPasswordExpirationWarning('Your password has expired. Please change it now.', 'expired');
                    } else if (expiration.days_remaining <= 7) {
                        this.showPasswordExpirationWarning(
                            `Your password expires in ${expiration.days_remaining} days. Please change it soon.`, 
                            'expiring_soon'
                        );
                    }
                }
                
                // Redirect after short delay (unless password is expired)
                if (!result.password_expiration?.expired) {
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                }
            } else {
                this.showError(result.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Login failed. Please check your connection and try again.');
        } finally {
            this.setSubmittingState(false);
        }
    }

    /**
     * Validate form
     */
    validateForm() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        let isValid = true;
        
        if (!username) {
            this.showFieldError('username', 'Username is required');
            isValid = false;
        }
        
        if (!password) {
            this.showFieldError('password', 'Password is required');
            isValid = false;
        }
        
        return isValid;
    }

    /**
     * Validate username
     */
    validateUsername() {
        const username = document.getElementById('username').value.trim();
        const field = document.getElementById('username');
        
        if (!username) {
            this.showFieldError('username', 'Username is required');
            return false;
        }
        
        if (username.length < 3) {
            this.showFieldError('username', 'Username must be at least 3 characters');
            return false;
        }
        
        this.clearFieldError('username');
        return true;
    }

    /**
     * Validate password
     */
    validatePassword() {
        const password = document.getElementById('password').value;
        const field = document.getElementById('password');
        
        if (!password) {
            this.showFieldError('password', 'Password is required');
            return false;
        }
        
        if (password.length < 6) {
            this.showFieldError('password', 'Password must be at least 6 characters');
            return false;
        }
        
        this.clearFieldError('password');
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
    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleButton = document.getElementById('passwordToggle');
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
        
        const submitText = document.getElementById('loginText');
        if (submitText) {
            submitText.textContent = submitting ? 'Logging in...' : 'Login';
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
        this.clearFieldError('password');
    }

    /**
     * Destroy component
     */
    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit);
        }
    }

    /**
     * Show password expiration warning
     */
    showPasswordExpirationWarning(message, type = 'expiring_soon') {
        const warningDiv = document.getElementById('passwordExpirationWarning');
        const messageSpan = document.getElementById('passwordExpirationMessage');
        
        if (warningDiv && messageSpan) {
            messageSpan.textContent = message;
            warningDiv.className = `alert alert-${type === 'expired' ? 'danger' : 'warning'}`;
            warningDiv.style.display = 'block';
            
            // Scroll to warning
            warningDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
} 