/**
 * Authentication Profile Management
 * Handles user profile management, settings, and account operations
 */

export default class AuthProfile {
    constructor(authCore) {
        this.authCore = authCore;
        this.profileForm = null;
        this.passwordForm = null;
        this.settingsForm = null;
        this.isInitialized = false;
        this.currentUser = null;
        this.changePasswordForm = null;
        this.profileData = null;
        this.avatarUpload = null;
        this.validationRules = {
            firstName: {
                required: true,
                minLength: 2,
                maxLength: 50
            },
            lastName: {
                required: true,
                minLength: 2,
                maxLength: 50
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            },
            phone: {
                pattern: /^[\+]?[1-9][\d]{0,15}$/
            },
            bio: {
                maxLength: 500
            },
            currentPassword: {
                required: true
            },
            newPassword: {
                required: true,
                minLength: 8,
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
            },
            confirmNewPassword: {
                required: true,
                matchField: 'newPassword'
            }
        };
    }

    /**
     * Initialize the profile management system
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('👤 Initializing Auth Profile Management...');
        
        try {
            // Initialize forms
            this.initializeForms();
            
            // Setup event handlers
            this.setupEventHandlers();
            
            // Load current user data
            await this.loadUserProfile();
            
            // Setup real-time validation
            this.setupRealTimeValidation();
            
            this.isInitialized = true;
            console.log('✅ Auth Profile Management initialized');
            
        } catch (error) {
            console.error('❌ Auth Profile Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize profile forms
     */
    initializeForms() {
        this.profileForm = document.getElementById('profileForm');
        this.changePasswordForm = document.getElementById('changePasswordForm');

        // Create forms if they don't exist
        if (!this.profileForm) {
            this.createProfileForm();
        }

        if (!this.changePasswordForm) {
            this.createChangePasswordForm();
        }
    }

    /**
     * Create profile form
     */
    createProfileForm() {
        const formHtml = `
            <form id="profileForm" class="needs-validation" novalidate>
                <div class="row">
                    <div class="col-md-3 text-center mb-4">
                        <div class="avatar-container">
                            <img id="profileAvatar" src="/static/images/default-avatar.png" 
                                 alt="Profile Avatar" class="rounded-circle img-thumbnail" 
                                 style="width: 150px; height: 150px; object-fit: cover;">
                            <div class="avatar-overlay">
                                <label for="avatarUpload" class="btn btn-sm btn-primary">
                                    <i class="fas fa-camera"></i>
                                </label>
                                <input type="file" id="avatarUpload" accept="image/*" style="display: none;">
                            </div>
                        </div>
                        <div class="mt-2">
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="removeAvatar">
                                <i class="fas fa-trash me-1"></i>Remove
                            </button>
                        </div>
                    </div>
                    <div class="col-md-9">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="firstName" class="form-label">First Name *</label>
                                <input type="text" class="form-control" id="firstName" name="firstName" required>
                                <div class="invalid-feedback">
                                    Please enter your first name.
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="lastName" class="form-label">Last Name *</label>
                                <input type="text" class="form-control" id="lastName" name="lastName" required>
                                <div class="invalid-feedback">
                                    Please enter your last name.
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address *</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                            <div class="invalid-feedback">
                                Please enter a valid email address.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="phone" class="form-label">Phone Number</label>
                            <input type="tel" class="form-control" id="phone" name="phone">
                            <div class="invalid-feedback">
                                Please enter a valid phone number.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="bio" class="form-label">Bio</label>
                            <textarea class="form-control" id="bio" name="bio" rows="3" 
                                      placeholder="Tell us about yourself..."></textarea>
                            <div class="invalid-feedback">
                                Bio must be less than 500 characters.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="location" class="form-label">Location</label>
                            <input type="text" class="form-control" id="location" name="location" 
                                   placeholder="City, Country">
                        </div>
                        <div class="mb-3">
                            <label for="website" class="form-label">Website</label>
                            <input type="url" class="form-control" id="website" name="website" 
                                   placeholder="https://example.com">
                        </div>
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <button type="button" class="btn btn-secondary me-md-2" id="cancelProfile">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary" id="saveProfile">
                                <i class="fas fa-save me-2"></i>Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        `;

        const container = document.getElementById('profileContainer') || document.body;
        container.innerHTML = formHtml;
        this.profileForm = document.getElementById('profileForm');
    }

    /**
     * Create change password form
     */
    createChangePasswordForm() {
        const formHtml = `
            <form id="changePasswordForm" class="needs-validation" novalidate>
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-key me-2"></i>Change Password
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="currentPassword" class="form-label">Current Password *</label>
                            <div class="input-group">
                                <input type="password" class="form-control" id="currentPassword" name="currentPassword" required>
                                <button class="btn btn-outline-secondary" type="button" id="toggleCurrentPassword">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                            <div class="invalid-feedback">
                                Please enter your current password.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="newPassword" class="form-label">New Password *</label>
                            <div class="input-group">
                                <input type="password" class="form-control" id="newPassword" name="newPassword" required>
                                <button class="btn btn-outline-secondary" type="button" id="toggleNewPassword">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                            <div class="form-text">
                                Password must be at least 8 characters with uppercase, lowercase, number, and special character.
                            </div>
                            <div class="invalid-feedback">
                                Password must meet the requirements.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="confirmNewPassword" class="form-label">Confirm New Password *</label>
                            <div class="input-group">
                                <input type="password" class="form-control" id="confirmNewPassword" name="confirmNewPassword" required>
                                <button class="btn btn-outline-secondary" type="button" id="toggleConfirmNewPassword">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                            <div class="invalid-feedback">
                                Passwords do not match.
                            </div>
                        </div>
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <button type="button" class="btn btn-secondary me-md-2" id="cancelPassword">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary" id="changePasswordSubmit">
                                <i class="fas fa-key me-2"></i>Change Password
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        `;

        const container = document.getElementById('passwordContainer') || document.body;
        container.innerHTML = formHtml;
        this.changePasswordForm = document.getElementById('changePasswordForm');
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Profile form submission
        if (this.profileForm) {
            this.profileForm.addEventListener('submit', (e) => this.handleProfileSubmit(e));
        }

        // Change password form submission
        if (this.changePasswordForm) {
            this.changePasswordForm.addEventListener('submit', (e) => this.handleChangePasswordSubmit(e));
        }

        // Cancel buttons
        this.setupCancelHandlers();

        // Password toggle buttons
        this.setupPasswordToggles();

        // Real-time validation
        this.setupRealTimeValidation();
    }

    /**
     * Setup cancel handlers
     */
    setupCancelHandlers() {
        const cancelButtons = [
            { id: 'cancelProfile', action: () => this.resetProfileForm() },
            { id: 'cancelPassword', action: () => this.resetPasswordForm() }
        ];

        cancelButtons.forEach(({ id, action }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', action);
            }
        });
    }

    /**
     * Setup password toggle buttons
     */
    setupPasswordToggles() {
        const toggleButtons = [
            { id: 'toggleCurrentPassword', target: 'currentPassword' },
            { id: 'toggleNewPassword', target: 'newPassword' },
            { id: 'toggleConfirmNewPassword', target: 'confirmNewPassword' }
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
        const inputs = document.querySelectorAll('input[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    /**
     * Setup avatar upload
     */
    setupAvatarUpload() {
        this.avatarUpload = document.getElementById('avatarUpload');
        if (this.avatarUpload) {
            this.avatarUpload.addEventListener('change', (e) => this.handleAvatarUpload(e));
        }

        const removeAvatarBtn = document.getElementById('removeAvatar');
        if (removeAvatarBtn) {
            removeAvatarBtn.addEventListener('click', () => this.removeAvatar());
        }
    }

    /**
     * Load profile data
     */
    async loadProfileData() {
        try {
            // Get auth core instance
            const authCore = this.authCore;
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const user = authCore.getCurrentUser();
            if (user) {
                this.profileData = user;
                this.populateProfileForm(user);
            } else {
                // Load from API if not in memory
                await this.loadProfileFromAPI();
            }

        } catch (error) {
            console.error('Failed to load profile data:', error);
            this.showErrorMessage('Failed to load profile data');
        }
    }

    /**
     * Load profile from API
     */
    async loadProfileFromAPI() {
        try {
            const authCore = this.authCore;
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            await authCore.loadUserProfile();
            const user = authCore.getCurrentUser();
            if (user) {
                this.profileData = user;
                this.populateProfileForm(user);
            }

        } catch (error) {
            console.error('Failed to load profile from API:', error);
            throw error;
        }
    }

    /**
     * Populate profile form with user data
     * @param {Object} user - User data
     */
    populateProfileForm(user) {
        const fields = [
            'firstName', 'lastName', 'email', 'phone', 'bio', 'location', 'website'
        ];

        fields.forEach(field => {
            const input = document.getElementById(field);
            if (input && user[field]) {
                input.value = user[field];
            }
        });

        // Set avatar
        if (user.avatar_url) {
            const avatar = document.getElementById('profileAvatar');
            if (avatar) {
                avatar.src = user.avatar_url;
            }
        }
    }

    /**
     * Handle profile form submission
     * @param {Event} e - Form submission event
     */
    async handleProfileSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.profileForm)) {
            return;
        }

        const formData = new FormData(this.profileForm);
        const profileData = {
            firstName: formData.get('firstName'),
            lastName: formData.get('lastName'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            bio: formData.get('bio'),
            location: formData.get('location'),
            website: formData.get('website')
        };

        // Show loading state
        this.setFormLoading(this.profileForm, true);

        try {
            const response = await fetch('/api/auth/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(profileData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccessMessage('Profile updated successfully!');
                this.profileData = { ...this.profileData, ...profileData };
                
                // Update auth core user data
                const authCore = this.authCore;
                if (authCore) {
                    authCore.currentUser = this.profileData;
                }
            } else {
                this.showErrorMessage(result.error || 'Failed to update profile');
            }

        } catch (error) {
            console.error('Profile update error:', error);
            this.showErrorMessage('An error occurred while updating profile');
        } finally {
            this.setFormLoading(this.profileForm, false);
        }
    }

    /**
     * Handle change password form submission
     * @param {Event} e - Form submission event
     */
    async handleChangePasswordSubmit(e) {
        e.preventDefault();

        if (!this.validateForm(this.changePasswordForm)) {
            return;
        }

        const formData = new FormData(this.changePasswordForm);
        const currentPassword = formData.get('currentPassword');
        const newPassword = formData.get('newPassword');
        const confirmNewPassword = formData.get('confirmNewPassword');

        if (newPassword !== confirmNewPassword) {
            this.showFieldError(document.getElementById('confirmNewPassword'), 'Passwords do not match');
            return;
        }

        // Show loading state
        this.setFormLoading(this.changePasswordForm, true);

        try {
            // Get auth core instance
            const authCore = this.authCore;
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const result = await authCore.changePassword(currentPassword, newPassword);

            if (result.success) {
                this.showSuccessMessage('Password changed successfully!');
                this.resetPasswordForm();
            } else {
                this.showErrorMessage(result.error || 'Failed to change password');
            }

        } catch (error) {
            console.error('Change password error:', error);
            this.showErrorMessage('An error occurred while changing password');
        } finally {
            this.setFormLoading(this.changePasswordForm, false);
        }
    }

    /**
     * Handle avatar upload
     * @param {Event} e - File input change event
     */
    async handleAvatarUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file
        if (!this.validateImageFile(file)) {
            return;
        }

        // Show loading state
        this.setAvatarLoading(true);

        try {
            const formData = new FormData();
            formData.append('avatar', file);

            const response = await fetch('/api/auth/profile/avatar', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Update avatar display
                const avatar = document.getElementById('profileAvatar');
                if (avatar) {
                    avatar.src = result.avatar_url;
                }

                // Update profile data
                if (this.profileData) {
                    this.profileData.avatar_url = result.avatar_url;
                }

                this.showSuccessMessage('Avatar updated successfully!');
            } else {
                this.showErrorMessage(result.error || 'Failed to upload avatar');
            }

        } catch (error) {
            console.error('Avatar upload error:', error);
            this.showErrorMessage('An error occurred while uploading avatar');
        } finally {
            this.setAvatarLoading(false);
        }
    }

    /**
     * Remove avatar
     */
    async removeAvatar() {
        if (!confirm('Are you sure you want to remove your avatar?')) {
            return;
        }

        this.setAvatarLoading(true);

        try {
            const response = await fetch('/api/auth/profile/avatar', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            const result = await response.json();

            if (response.ok) {
                // Reset avatar to default
                const avatar = document.getElementById('profileAvatar');
                if (avatar) {
                    avatar.src = '/static/images/default-avatar.png';
                }

                // Update profile data
                if (this.profileData) {
                    this.profileData.avatar_url = null;
                }

                this.showSuccessMessage('Avatar removed successfully!');
            } else {
                this.showErrorMessage(result.error || 'Failed to remove avatar');
            }

        } catch (error) {
            console.error('Avatar removal error:', error);
            this.showErrorMessage('An error occurred while removing avatar');
        } finally {
            this.setAvatarLoading(false);
        }
    }

    /**
     * Validate image file
     * @param {File} file - File to validate
     * @returns {boolean} Validation result
     */
    validateImageFile(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

        if (file.size > maxSize) {
            this.showErrorMessage('Image file size must be less than 5MB');
            return false;
        }

        if (!allowedTypes.includes(file.type)) {
            this.showErrorMessage('Please select a valid image file (JPEG, PNG, GIF, WebP)');
            return false;
        }

        return true;
    }

    /**
     * Reset profile form
     */
    resetProfileForm() {
        if (this.profileData) {
            this.populateProfileForm(this.profileData);
        }
        this.clearFormErrors(this.profileForm);
    }

    /**
     * Reset password form
     */
    resetPasswordForm() {
        if (this.changePasswordForm) {
            this.changePasswordForm.reset();
            this.clearFormErrors(this.changePasswordForm);
        }
    }

    /**
     * Validate form
     * @param {HTMLFormElement} form - Form to validate
     * @returns {boolean} Validation result
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
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
     * Clear form errors
     * @param {HTMLFormElement} form - Form element
     */
    clearFormErrors(form) {
        const inputs = form.querySelectorAll('.is-invalid');
        inputs.forEach(input => this.clearFieldError(input));
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
     * Set avatar loading state
     * @param {boolean} loading - Loading state
     */
    setAvatarLoading(loading) {
        const avatar = document.getElementById('profileAvatar');
        const removeBtn = document.getElementById('removeAvatar');
        
        if (avatar) {
            if (loading) {
                avatar.style.opacity = '0.5';
            } else {
                avatar.style.opacity = '1';
            }
        }

        if (removeBtn) {
            removeBtn.disabled = loading;
        }
    }

    /**
     * Get authentication token
     * @returns {string|null} Auth token
     */
    getAuthToken() {
        const authCore = this.authCore;
        return authCore ? authCore.getSessionToken() : null;
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
     * Refresh profile data
     */
    async refreshProfile() {
        await this.loadProfileData();
    }

    /**
     * Destroy profile management
     */
    destroy() {
        // Remove event listeners
        if (this.profileForm) {
            this.profileForm.removeEventListener('submit', this.handleProfileSubmit);
        }

        if (this.changePasswordForm) {
            this.changePasswordForm.removeEventListener('submit', this.handleChangePasswordSubmit);
        }

        if (this.avatarUpload) {
            this.avatarUpload.removeEventListener('change', this.handleAvatarUpload);
        }

        this.isInitialized = false;
        console.log('🧹 Profile Management destroyed');
    }
} 