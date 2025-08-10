/**
 * User Preferences Management Module
 * Handles user preferences UI and API interactions
 * CACHE BUST: 2025-08-10-20:07
 */

export default class UserPreferences {
    constructor(authCore) {
        this.authCore = authCore;
        this.preferences = {};
        this.preferencesForm = null;
        this.isLoading = false;
    }

    /**
     * Initialize preferences management
     */
    async init() {
        try {
            await this.loadPreferences();
            this.createPreferencesForm();
            this.setupEventHandlers();
            this.populateForm();
        } catch (error) {
            console.error('Error initializing preferences:', error);
        }
    }

    /**
     * Load user preferences from API
     */
    async loadPreferences() {
        try {
            const token = this.getAuthToken();
            console.log('Loading preferences with token:', token ? 'available' : 'not available');
            
            if (!token) {
                console.warn('No auth token available, using default preferences');
                this.preferences = {};
                return;
            }
            
            const response = await fetch('/api/auth/preferences', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log('Preferences API response status:', response.status);
            
            if (response.ok) {
                const result = await response.json();
                console.log('Preferences loaded:', result);
                this.preferences = result.preferences || {};
            } else {
                console.error('Failed to load preferences, status:', response.status);
                const errorText = await response.text();
                console.error('Error response:', errorText);
                this.preferences = {};
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
            this.preferences = {};
        }
    }

    /**
     * Create preferences form
     */
    createPreferencesForm() {
        const formHtml = `
            <form id="preferencesForm" class="needs-validation" novalidate>
                <div class="row">
                    <!-- UI/UX Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-palette me-2"></i>UI/UX Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="theme" class="form-label">Theme</label>
                                    <select class="form-select" id="theme" name="theme">
                                        <option value="light">Light</option>
                                        <option value="dark">Dark</option>
                                        <option value="auto">Auto</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="language" class="form-label">Language</label>
                                    <select class="form-select" id="language" name="language">
                                        <option value="en">English</option>
                                        <option value="es">Español</option>
                                        <option value="fr">Français</option>
                                        <option value="de">Deutsch</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="timezone" class="form-label">Timezone</label>
                                    <select class="form-select" id="timezone" name="timezone">
                                        <option value="UTC">UTC</option>
                                        <option value="America/New_York">Eastern Time</option>
                                        <option value="America/Chicago">Central Time</option>
                                        <option value="America/Denver">Mountain Time</option>
                                        <option value="America/Los_Angeles">Pacific Time</option>
                                        <option value="Europe/London">London</option>
                                        <option value="Europe/Paris">Paris</option>
                                        <option value="Asia/Tokyo">Tokyo</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="dateFormat" class="form-label">Date Format</label>
                                    <select class="form-select" id="dateFormat" name="date_format">
                                        <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                                        <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                                        <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="timeFormat" class="form-label">Time Format</label>
                                    <select class="form-select" id="timeFormat" name="time_format">
                                        <option value="24h">24-hour</option>
                                        <option value="12h">12-hour</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Notification Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-bell me-2"></i>Notification Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="emailNotifications" name="email_notifications">
                                        <label class="form-check-label" for="emailNotifications">
                                            Email Notifications
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="smsNotifications" name="sms_notifications">
                                        <label class="form-check-label" for="smsNotifications">
                                            SMS Notifications
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="pushNotifications" name="push_notifications">
                                        <label class="form-check-label" for="pushNotifications">
                                            Push Notifications
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="notificationFrequency" class="form-label">Notification Frequency</label>
                                    <select class="form-select" id="notificationFrequency" name="notification_frequency">
                                        <option value="immediate">Immediate</option>
                                        <option value="daily">Daily</option>
                                        <option value="weekly">Weekly</option>
                                        <option value="never">Never</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Privacy Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-shield-alt me-2"></i>Privacy Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="profileVisibility" class="form-label">Profile Visibility</label>
                                    <select class="form-select" id="profileVisibility" name="profile_visibility">
                                        <option value="private">Private</option>
                                        <option value="public">Public</option>
                                        <option value="friends">Friends Only</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="dataSharing" name="data_sharing">
                                        <label class="form-check-label" for="dataSharing">
                                            Allow Data Sharing
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="analyticsTracking" name="analytics_tracking">
                                        <label class="form-check-label" for="analyticsTracking">
                                            Analytics Tracking
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Security Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-lock me-2"></i>Security Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="sessionTimeout" class="form-label">Session Timeout (minutes)</label>
                                    <input type="number" class="form-control" id="sessionTimeout" name="session_timeout" min="5" max="480">
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="requireMfa" name="require_mfa">
                                        <label class="form-check-label" for="requireMfa">
                                            Require MFA
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="loginNotifications" name="login_notifications">
                                        <label class="form-check-label" for="loginNotifications">
                                            Login Notifications
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Application Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-cog me-2"></i>Application Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="defaultPageSize" class="form-label">Default Page Size</label>
                                    <select class="form-select" id="defaultPageSize" name="default_page_size">
                                        <option value="10">10</option>
                                        <option value="20">20</option>
                                        <option value="50">50</option>
                                        <option value="100">100</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="autoSave" name="auto_save">
                                        <label class="form-check-label" for="autoSave">
                                            Auto Save
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="showTutorials" name="show_tutorials">
                                        <label class="form-check-label" for="showTutorials">
                                            Show Tutorials
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="compactMode" name="compact_mode">
                                        <label class="form-check-label" for="compactMode">
                                            Compact Mode
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Communication Preferences -->
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-envelope me-2"></i>Communication Preferences
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="emailDigest" name="email_digest">
                                        <label class="form-check-label" for="emailDigest">
                                            Email Digest
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="digestFrequency" class="form-label">Digest Frequency</label>
                                    <select class="form-select" id="digestFrequency" name="digest_frequency">
                                        <option value="daily">Daily</option>
                                        <option value="weekly">Weekly</option>
                                        <option value="monthly">Monthly</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="marketingEmails" name="marketing_emails">
                                        <label class="form-check-label" for="marketingEmails">
                                            Marketing Emails
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <button type="button" class="btn btn-secondary me-md-2" id="resetPreferences">
                        <i class="fas fa-undo me-2"></i>Reset to Default
                    </button>
                    <button type="submit" class="btn btn-primary" id="savePreferences">
                        <i class="fas fa-save me-2"></i>Save Preferences
                    </button>
                </div>
            </form>
        `;

        // Insert form into the page
        const container = document.getElementById('preferencesContainer');
        if (container) {
            container.innerHTML = formHtml;
            this.preferencesForm = document.getElementById('preferencesForm');
        }
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        if (!this.preferencesForm) return;

        // Form submission
        this.preferencesForm.addEventListener('submit', (e) => this.handleSubmit(e));

        // Reset preferences
        const resetBtn = document.getElementById('resetPreferences');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetPreferences());
        }
    }

    /**
     * Populate form with current preferences
     */
    populateForm() {
        if (!this.preferencesForm) return;

        // Populate form fields
        Object.keys(this.preferences).forEach(key => {
            const element = this.preferencesForm.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = this.preferences[key];
                } else {
                    element.value = this.preferences[key];
                }
            }
        });
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        e.preventDefault();

        if (this.isLoading) return;

        this.setFormLoading(true);

        try {
            const formData = new FormData(this.preferencesForm);
            const preferences = {};

            // Collect form data
            for (const [key, value] of formData.entries()) {
                const element = this.preferencesForm.querySelector(`[name="${key}"]`);
                if (element.type === 'checkbox') {
                    preferences[key] = element.checked;
                } else if (element.type === 'number') {
                    preferences[key] = parseInt(value);
                } else {
                    preferences[key] = value;
                }
            }

            // Send to API
            const response = await fetch('/api/auth/preferences', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(preferences)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccessMessage('Preferences updated successfully!');
                this.preferences = { ...this.preferences, ...preferences };
            } else {
                this.showErrorMessage(result.error || 'Failed to update preferences');
            }

        } catch (error) {
            console.error('Preferences update error:', error);
            this.showErrorMessage('An error occurred while updating preferences');
        } finally {
            this.setFormLoading(false);
        }
    }

    /**
     * Reset preferences to default
     */
    async resetPreferences() {
        if (!confirm('Are you sure you want to reset all preferences to default?')) {
            return;
        }

        this.setFormLoading(true);

        try {
            const response = await fetch('/api/auth/preferences', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccessMessage('Preferences reset to default successfully!');
                await this.loadPreferences();
                this.populateForm();
            } else {
                this.showErrorMessage(result.error || 'Failed to reset preferences');
            }

        } catch (error) {
            console.error('Preferences reset error:', error);
            this.showErrorMessage('An error occurred while resetting preferences');
        } finally {
            this.setFormLoading(false);
        }
    }

    /**
     * Set form loading state
     */
    setFormLoading(loading) {
        this.isLoading = loading;
        const submitBtn = document.getElementById('savePreferences');
        const resetBtn = document.getElementById('resetPreferences');

        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.innerHTML = loading 
                ? '<i class="fas fa-spinner fa-spin me-2"></i>Saving...' 
                : '<i class="fas fa-save me-2"></i>Save Preferences';
        }

        if (resetBtn) {
            resetBtn.disabled = loading;
        }
    }

    /**
     * Get auth token
     */
    getAuthToken() {
        const authCore = this.authCore;
        return authCore ? authCore.getSessionToken() : null;
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        if (this.authCore && this.authCore.showSuccessMessage) {
            this.authCore.showSuccessMessage(message);
        } else {
            alert(message);
        }
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        if (this.authCore && this.authCore.showErrorMessage) {
            this.authCore.showErrorMessage(message);
        } else {
            alert(message);
        }
    }

    /**
     * Destroy preferences management
     */
    destroy() {
        if (this.preferencesForm) {
            this.preferencesForm.removeEventListener('submit', this.handleSubmit);
        }
    }
} 