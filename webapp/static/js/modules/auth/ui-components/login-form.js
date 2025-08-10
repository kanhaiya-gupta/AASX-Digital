/**
 * Login Form Handler
 * Integrates with AuthUIManager for proper authentication flow
 * CACHE BUST: 2025-08-10-20:07
 */
export class LoginForm {
    constructor() {
        console.log('🔍 Creating LoginForm instance');
        this.form = document.getElementById('loginForm');
        this.isSubmitting = false;
        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
            console.log('✅ Login form initialized');
        } else {
            console.error('❌ Login form not found');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;

        const username = document.getElementById('login_username').value;
        const password = document.getElementById('login_password').value;
        const rememberMe = document.getElementById('login_rememberMe')?.checked || false;

        console.log('🔐 Login form submitted:', { username, rememberMe });

        if (!username || !password) {
            this.showError('Please enter both username and password');
            return;
        }

        this.setSubmittingState(true);
        this.clearAlerts();

        try {
            console.log('📡 Sending login request to /api/auth/login...');
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            console.log('📡 Login response status:', response.status);
            const result = await response.json();
            console.log('📡 Login response data:', result);

            if (response.ok) {
                console.log('✅ Login successful, storing token...');
                // Store token with correct key
                localStorage.setItem('auth_token', result.access_token);
                console.log('💾 Token stored in localStorage:', result.access_token ? 'YES' : 'NO');
                console.log('💾 Token value preview:', result.access_token ? result.access_token.substring(0, 20) + '...' : 'NO TOKEN');
                
                // Show success message
                this.showSuccess('Login successful!');
                
                // Use AuthUIManager to handle the login (NO page redirect)
                if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
                    console.log('✅ CoreModule and AuthUIManager available');
                    // Create user object from response
                    const user = {
                        username: username,
                        email: result.user?.email || '',
                        role: result.user?.role || 'user',
                        permissions: result.user?.permissions || []
                    };
                    
                    // Let AuthUIManager handle the UI update - pass the STORED token value
                    const storedToken = localStorage.getItem('auth_token');
                    console.log('🔑 Passing stored token to AuthUIManager:', storedToken ? 'YES' : 'NO');
                    await window.CoreModule.components.authUI.handleUserLogin(user, storedToken, rememberMe);
                    console.log('✅ Login handled by AuthUIManager with stored token');
                } else {
                    console.warn('⚠️ CoreModule not ready, waiting for it...');
                    // Wait for CoreModule to be ready
                    window.addEventListener('coreModuleReady', async () => {
                        if (window.CoreModule && window.CoreModule.components && window.CoreModule.components.authUI) {
                            const user = {
                                username: username,
                                email: result.user?.email || '',
                                role: result.user?.role || 'user',
                                permissions: result.user?.permissions || []
                            };
                            const storedToken = localStorage.getItem('auth_token');
                            await window.CoreModule.components.authUI.handleUserLogin(user, storedToken, rememberMe);
                            console.log('✅ Login handled by AuthUIManager after waiting');
                        } else {
                            console.warn('⚠️ AuthUIManager still not available, updating UI manually');
                            this.updateUIManually();
                        }
                    });
                }
                
            } else {
                console.error('❌ Login failed:', result.error);
                this.showError(result.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('❌ Login error:', error);
            this.showError('Login failed. Please check your connection and try again.');
        } finally {
            this.setSubmittingState(false);
        }
    }

    updateUIManually() {
        // Simple fallback UI update if AuthUIManager is not available
        const authenticatedMenu = document.getElementById('authenticatedMenu');
        const unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
        const userDisplayName = document.getElementById('userDisplayName');
        
        if (authenticatedMenu && unauthenticatedMenu) {
            authenticatedMenu.style.display = 'block';
            unauthenticatedMenu.style.display = 'none';
        }
        
        if (userDisplayName) {
            userDisplayName.textContent = document.getElementById('login_username').value;
        }
        
        console.log('✅ UI updated manually');
    }

    setSubmittingState(submitting) {
        this.isSubmitting = submitting;
        const loginBtn = document.getElementById('loginBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const loginText = document.getElementById('loginText');

        if (submitting) {
            loginBtn.disabled = true;
            loadingSpinner.style.display = 'inline-block';
            loginText.style.display = 'none';
        } else {
            loginBtn.disabled = false;
            loadingSpinner.style.display = 'none';
            loginText.style.display = 'inline';
        }
    }

    showSuccess(message) {
        const successAlert = document.getElementById('successAlert') || this.createAlert('success', message);
        successAlert.style.display = 'block';
        successAlert.textContent = message;
    }

    showError(message) {
        const errorAlert = document.getElementById('errorAlert') || this.createAlert('error', message);
        errorAlert.style.display = 'block';
        errorAlert.textContent = message;
    }

    createAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.id = type === 'success' ? 'successAlert' : 'errorAlert';
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        alertDiv.style.display = 'none';
        alertDiv.textContent = message;
        
        // Insert after the form
        this.form.parentNode.insertBefore(alertDiv, this.form.nextSibling);
        return alertDiv;
    }

    clearAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => alert.style.display = 'none');
    }

    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit.bind(this));
        }
        console.log('✅ Login form destroyed');
    }
}