/**
 * Authentication Login Management Module
 * Handles login forms, validation, and UI interactions
 */

export default class AuthLogin {
    constructor() {
        this.isInitialized = false;
        this.loginForm = null;
        this.forgotPasswordForm = null;
        this.resetPasswordForm = null;
        this.verificationForm = null;
        this.currentStep = 'login'; // login, forgot-password, reset-password, verification
        this.validationRules = {
            username: {
                required: true,
                minLength: 3,
                maxLength: 50
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            },
            password: {
                required: true,
                minLength: 8,
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
            },
            confirmPassword: {
                required: true,
                matchField: 'password'
            }
        };
    }

    /**
     * Initialize Login Management
     */
    async init() {
        console.log('🔐 Initializing Login Management...');

        try {
            // Initialize forms
            this.initializeForms();

            // Setup event handlers
            this.setupEventHandlers();

            // Setup validation
            this.setupValidation();

            // Check for verification tokens in URL
            this.checkVerificationTokens();

            this.isInitialized = true;
            console.log('✅ Login Management initialized');

        } catch (error) {
            console.error('❌ Login Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize login forms
     */
    initializeForms() {
        this.loginForm = document.getElementById('loginForm');
        this.forgotPasswordForm = document.getElementById('forgotPasswordForm');
        this.resetPasswordForm = document.getElementById('resetPasswordForm');
        this.verificationForm = document.getElementById('verificationForm');

        // Create forms if they don't exist
        if (!this.loginForm) {
            this.createLoginForm();
        }

        if (!this.forgotPasswordForm) {
            this.createForgotPasswordForm();
        }

        if (!this.resetPasswordForm) {
            this.createResetPasswordForm();
        }

        if (!this.verificationForm) {
            this.createVerificationForm();
        }
    }

    /**
     * Create login form
     */
    createLoginForm() {
        const formHtml = `
            <form id="loginForm" class="needs-validation" novalidate>
                <div class="mb-3">
                    <label for="loginUsername" class="form-label">Username or Email</label>
                    <input type="text" class="form-control" id="loginUsername" name="username" required>
                    <div class="invalid-feedback">
                        Please enter a valid username or email.
                    </div>
                </div>
                <div class="mb-3">
                    <label for="loginPassword" class="form-label">Password</label>
                    <div class="input-group">
                        <input type="password" class="form-control" id="loginPassword" name="password" required>
                        <button class="btn btn-outline-secondary" type="button" id="togglePassword">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">
                        Please enter your password.
                    </div>
                </div>
                <div class="mb-3 form-check">
                    <input type="checkbox" class="form-check-input" id="rememberMe" name="rememberMe">
                    <label class="form-check-label" for="rememberMe">
                        Remember me
                    </label>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" id="loginSubmit">
                        <i class="fas fa-sign-in-alt me-2"></i>Login
                    </button>
                </div>
                <div class="text-center mt-3">
                    <a href="#" id="forgotPasswordLink" class="text-decoration-none">Forgot Password?</a>
                </div>
                <div class="text-center mt-2">
                    <span class="text-muted">Don't have an account?</span>
                    <a href="#" id="registerLink" class="text-decoration-none ms-1">Register</a>
                </div>
            </form>
        `;

        const container = document.getElementById('authContainer') || document.body;
        container.innerHTML = formHtml;
        this.loginForm = document.getElementById('loginForm');
    }

    /**
     * Create forgot password form
     */
    createForgotPasswordForm() {
        const formHtml = `
            <form id="forgotPasswordForm" class="needs-validation" novalidate style="display: none;">
                <div class="text-center mb-4">
                    <h4>Reset Password</h4>
                    <p class="text-muted">Enter your email address to receive a password reset link.</p>
                </div>
                <div class="mb-3">
                    <label for="resetEmail" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="resetEmail" name="email" required>
                    <div class="invalid-feedback">
                        Please enter a valid email address.
                    </div>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" id="resetPasswordSubmit">
                        <i class="fas fa-paper-plane me-2"></i>Send Reset Link
                    </button>
                </div>
                <div class="text-center mt-3">
                    <a href="#" id="backToLoginLink" class="text-decoration-none">
                        <i class="fas fa-arrow-left me-1"></i>Back to Login
                    </a>
                </div>
            </form>
        `;

        const container = document.getElementById('authContainer') || document.body;
        container.insertAdjacentHTML('beforeend', formHtml);
        this.forgotPasswordForm = document.getElementById('forgotPasswordForm');
    }

    /**
     * Create reset password form
     */
    createResetPasswordForm() {
        const formHtml = `
            <form id="resetPasswordForm" class="needs-validation" novalidate style="display: none;">
                <div class="text-center mb-4">
                    <h4>Set New Password</h4>
                    <p class="text-muted">Enter your new password below.</p>
                </div>
                <div class="mb-3">
                    <label for="newPassword" class="form-label">New Password</label>
                    <div class="input-group">
                        <input type="password" class="form-control" id="newPassword" name="newPassword" required>
                        <button class="btn btn-outline-secondary" type="button" id="toggleNewPassword">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">
                        Password must be at least 8 characters with uppercase, lowercase, number, and special character.
                    </div>
                </div>
                <div class="mb-3">
                    <label for="confirmNewPassword" class="form-label">Confirm New Password</label>
                    <div class="input-group">
                        <input type="password" class="form-control" id="confirmNewPassword" name="confirmNewPassword" required>
                        <button class="btn btn-outline-secondary" type="button" id="toggleConfirmPassword">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">
                        Passwords do not match.
                    </div>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" id="setNewPasswordSubmit">
                        <i class="fas fa-key me-2"></i>Set New Password
                    </button>
                </div>
                <div class="text-center mt-3">
                    <a href="#" id="backToLoginFromResetLink" class="text-decoration-none">
                        <i class="fas fa-arrow-left me-1"></i>Back to Login
                    </a>
                </div>
            </form>
        `;

        const container = document.getElementById('authContainer') || document.body;
        container.insertAdjacentHTML('beforeend', formHtml);
        this.resetPasswordForm = document.getElementById('resetPasswordForm');
    }

    /**
     * Create verification form
     */
    createVerificationForm() {
        const formHtml = `
            <form id="verificationForm" class="needs-validation" novalidate style="display: none;">
                <div class="text-center mb-4">
                    <h4>Email Verification</h4>
                    <p class="text-muted">Please verify your email address to complete registration.</p>
                </div>
                <div class="mb-3">
                    <label for="verificationToken" class="form-label">Verification Token</label>
                    <input type="text" class="form-control" id="verificationToken" name="token" required>
                    <div class="invalid-feedback">
                        Please enter the verification token.
                    </div>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" id="verifyEmailSubmit">
                        <i class="fas fa-check me-2"></i>Verify Email
                    </button>
                </div>
                <div class="text-center mt-3">
                    <a href="#" id="backToLoginFromVerifyLink" class="text-decoration-none">
                        <i class="fas fa-arrow-left me-1"></i>Back to Login
                    </a>
                </div>
            </form>
        `;

        const container = document.getElementById('authContainer') || document.body;
        container.insertAdjacentHTML('beforeend', formHtml);
        this.verificationForm = document.getElementById('verificationForm');
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Login form submission
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLoginSubmit(e));
        }

        // Forgot password form submission
        if (this.forgotPasswordForm) {
            this.forgotPasswordForm.addEventListener('submit', (e) => this.handleForgotPasswordSubmit(e));
        }

        // Reset password form submission
        if (this.resetPasswordForm) {
            this.resetPasswordForm.addEventListener('submit', (e) => this.handleResetPasswordSubmit(e));
        }

        // Verification form submission
        if (this.verificationForm) {
            this.verificationForm.addEventListener('submit', (e) => this.handleVerificationSubmit(e));
        }

        // Navigation links
        this.setupNavigationHandlers();

        // Password toggle buttons
        this.setupPasswordToggles();

        // Real-time validation
        this.setupRealTimeValidation();
    }

    /**
     * Setup navigation handlers
     */
    setupNavigationHandlers() {
        // Forgot password link
        const forgotPasswordLink = document.getElementById('forgotPasswordLink');
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showForgotPasswordForm();
            });
        }

        // Back to login links
        const backToLoginLinks = [
            'backToLoginLink',
            'backToLoginFromResetLink',
            'backToLoginFromVerifyLink'
        ];

        backToLoginLinks.forEach(id => {
            const link = document.getElementById(id);
            if (link) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showLoginForm();
                });
            }
        });

        // Register link
        const registerLink = document.getElementById('registerLink');
        if (registerLink) {
            registerLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.redirectToRegister();
            });
        }
    }

    /**
     * Setup password toggle buttons
     */
    setupPasswordToggles() {
        const toggleButtons = [
            { id: 'togglePassword', target: 'loginPassword' },
            { id: 'toggleNewPassword', target: 'newPassword' },
            { id: 'toggleConfirmPassword', target: 'confirmNewPassword' }
        ];

        toggleButtons.forEach(({ id, target }) => {
            const button = document.getElementById(id);
            const input = document.getElementById(target);
            
            if (button && input) {
                button.addEventListener('click', () => {
                    const type = input.type === 'password' ? 'text' : 'password';
                    input.type = type;
                    const icon = button.querySelector('i');
                    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
                });
            }
        });
    }

    /**
     * Setup real-time validation
     */
    setupRealTimeValidation() {
        const inputs = document.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    /**
     * Handle login form submission
     * @param {Event} e - Form submission event
     */
    async handleLoginSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.loginForm)) {
            return;
        }

        const formData = new FormData(this.loginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        const rememberMe = formData.get('rememberMe') === 'on';

        // Show loading state
        this.setFormLoading(this.loginForm, true);

        try {
            // Get auth core instance
            const authCore = window.AuthModule?.getCore();
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const result = await authCore.login(username, password, rememberMe);

            if (result.success) {
                this.showSuccessMessage('Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                this.showErrorMessage(result.error || 'Login failed');
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showErrorMessage('An error occurred during login');
        } finally {
            this.setFormLoading(this.loginForm, false);
        }
    }

    /**
     * Handle forgot password form submission
     * @param {Event} e - Form submission event
     */
    async handleForgotPasswordSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.forgotPasswordForm)) {
            return;
        }

        const formData = new FormData(this.forgotPasswordForm);
        const email = formData.get('email');

        // Show loading state
        this.setFormLoading(this.forgotPasswordForm, true);

        try {
            // Get auth core instance
            const authCore = window.AuthModule?.getCore();
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const result = await authCore.resetPassword(email);

            if (result.success) {
                this.showSuccessMessage('Password reset email sent! Check your inbox.');
                this.showLoginForm();
            } else {
                this.showErrorMessage(result.error || 'Failed to send reset email');
            }

        } catch (error) {
            console.error('Forgot password error:', error);
            this.showErrorMessage('An error occurred while sending reset email');
        } finally {
            this.setFormLoading(this.forgotPasswordForm, false);
        }
    }

    /**
     * Handle reset password form submission
     * @param {Event} e - Form submission event
     */
    async handleResetPasswordSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.resetPasswordForm)) {
            return;
        }

        const formData = new FormData(this.resetPasswordForm);
        const newPassword = formData.get('newPassword');
        const confirmNewPassword = formData.get('confirmNewPassword');

        if (newPassword !== confirmNewPassword) {
            this.showFieldError(document.getElementById('confirmNewPassword'), 'Passwords do not match');
            return;
        }

        // Show loading state
        this.setFormLoading(this.resetPasswordForm, true);

        try {
            // Get reset token from URL
            const urlParams = new URLSearchParams(window.location.search);
            const resetToken = urlParams.get('token');

            if (!resetToken) {
                throw new Error('Reset token not found');
            }

            // Call API to reset password
            const response = await fetch('/api/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: resetToken,
                    new_password: newPassword
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccessMessage('Password reset successful! You can now login.');
                this.showLoginForm();
            } else {
                this.showErrorMessage(result.error || 'Failed to reset password');
            }

        } catch (error) {
            console.error('Reset password error:', error);
            this.showErrorMessage('An error occurred while resetting password');
        } finally {
            this.setFormLoading(this.resetPasswordForm, false);
        }
    }

    /**
     * Handle verification form submission
     * @param {Event} e - Form submission event
     */
    async handleVerificationSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.verificationForm)) {
            return;
        }

        const formData = new FormData(this.verificationForm);
        const token = formData.get('token');

        // Show loading state
        this.setFormLoading(this.verificationForm, true);

        try {
            // Get auth core instance
            const authCore = window.AuthModule?.getCore();
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const result = await authCore.verifyEmail(token);

            if (result.success) {
                this.showSuccessMessage('Email verified successfully! You can now login.');
                this.showLoginForm();
            } else {
                this.showErrorMessage(result.error || 'Email verification failed');
            }

        } catch (error) {
            console.error('Verification error:', error);
            this.showErrorMessage('An error occurred during email verification');
        } finally {
            this.setFormLoading(this.verificationForm, false);
        }
    }

    /**
     * Show login form
     */
    showLoginForm() {
        this.hideAllForms();
        if (this.loginForm) {
            this.loginForm.style.display = 'block';
        }
        this.currentStep = 'login';
    }

    /**
     * Show forgot password form
     */
    showForgotPasswordForm() {
        this.hideAllForms();
        if (this.forgotPasswordForm) {
            this.forgotPasswordForm.style.display = 'block';
        }
        this.currentStep = 'forgot-password';
    }

    /**
     * Show reset password form
     */
    showResetPasswordForm() {
        this.hideAllForms();
        if (this.resetPasswordForm) {
            this.resetPasswordForm.style.display = 'block';
        }
        this.currentStep = 'reset-password';
    }

    /**
     * Show verification form
     */
    showVerificationForm() {
        this.hideAllForms();
        if (this.verificationForm) {
            this.verificationForm.style.display = 'block';
        }
        this.currentStep = 'verification';
    }

    /**
     * Hide all forms
     */
    hideAllForms() {
        const forms = [this.loginForm, this.forgotPasswordForm, this.resetPasswordForm, this.verificationForm];
        forms.forEach(form => {
            if (form) {
                form.style.display = 'none';
            }
        });
    }

    /**
     * Check for verification tokens in URL
     */
    checkVerificationTokens() {
        const urlParams = new URLSearchParams(window.location.search);
        const resetToken = urlParams.get('token');
        const verifyToken = urlParams.get('verify');

        if (resetToken) {
            this.showResetPasswordForm();
        } else if (verifyToken) {
            document.getElementById('verificationToken').value = verifyToken;
            this.showVerificationForm();
        }
    }

    /**
     * Redirect to register page
     */
    redirectToRegister() {
        window.location.href = '/auth/register';
    }

    /**
     * Validate form
     * @param {HTMLFormElement} form - Form to validate
     * @returns {boolean} Validation result
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Validate field
     * @param {HTMLInputElement} input - Input field to validate
     * @returns {boolean} Validation result
     */
    validateField(input) {
        const value = input.value.trim();
        const fieldName = input.name;
        const rules = this.validationRules[fieldName];

        if (!rules) {
            return true;
        }

        // Required validation
        if (rules.required && !value) {
            this.showFieldError(input, `${this.getFieldLabel(input)} is required`);
            return false;
        }

        // Min length validation
        if (rules.minLength && value.length < rules.minLength) {
            this.showFieldError(input, `${this.getFieldLabel(input)} must be at least ${rules.minLength} characters`);
            return false;
        }

        // Max length validation
        if (rules.maxLength && value.length > rules.maxLength) {
            this.showFieldError(input, `${this.getFieldLabel(input)} must be no more than ${rules.maxLength} characters`);
            return false;
        }

        // Pattern validation
        if (rules.pattern && !rules.pattern.test(value)) {
            this.showFieldError(input, `${this.getFieldLabel(input)} format is invalid`);
            return false;
        }

        // Match field validation
        if (rules.matchField) {
            const matchInput = document.querySelector(`[name="${rules.matchField}"]`);
            if (matchInput && value !== matchInput.value) {
                this.showFieldError(input, `${this.getFieldLabel(input)} does not match`);
                return false;
            }
        }

        this.clearFieldError(input);
        return true;
    }

    /**
     * Show field error
     * @param {HTMLInputElement} input - Input field
     * @param {string} message - Error message
     */
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
        }
    }

    /**
     * Clear field error
     * @param {HTMLInputElement} input - Input field
     */
    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = '';
        }
    }

    /**
     * Get field label
     * @param {HTMLInputElement} input - Input field
     * @returns {string} Field label
     */
    getFieldLabel(input) {
        const label = input.parentNode.querySelector('label');
        return label ? label.textContent.replace('*', '').trim() : input.name;
    }

    /**
     * Set form loading state
     * @param {HTMLFormElement} form - Form element
     * @param {boolean} loading - Loading state
     */
    setFormLoading(form, loading) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = loading;
            const icon = submitButton.querySelector('i');
            if (icon) {
                icon.className = loading ? 'fas fa-spinner fa-spin me-2' : icon.className;
            }
            submitButton.innerHTML = loading ? 
                '<i class="fas fa-spinner fa-spin me-2"></i>Processing...' : 
                submitButton.innerHTML;
        }
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccessMessage(message) {
        // Use shared alerts if available
        if (window.showSuccessAlert) {
            window.showSuccessAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showErrorMessage(message) {
        // Use shared alerts if available
        if (window.showErrorAlert) {
            window.showErrorAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Refresh login status
     */
    async refreshLoginStatus() {
        // Check if user is already logged in
        const authCore = window.AuthModule?.getCore();
        if (authCore && authCore.isUserAuthenticated()) {
            // Redirect to dashboard if already logged in
            window.location.href = '/dashboard';
        }
    }

    /**
     * Destroy login management
     */
    destroy() {
        // Remove event listeners
        if (this.loginForm) {
            this.loginForm.removeEventListener('submit', this.handleLoginSubmit);
        }

        if (this.forgotPasswordForm) {
            this.forgotPasswordForm.removeEventListener('submit', this.handleForgotPasswordSubmit);
        }

        if (this.resetPasswordForm) {
            this.resetPasswordForm.removeEventListener('submit', this.handleResetPasswordSubmit);
        }

        if (this.verificationForm) {
            this.verificationForm.removeEventListener('submit', this.handleVerificationSubmit);
        }

        this.isInitialized = false;
        console.log('🧹 Login Management destroyed');
    }
} 