/**
 * User Context Display Component
 * =============================
 * 
 * This component displays user context information including user type,
 * permissions, and organization details.
 */

class UserContextDisplay {
    constructor() {
        this.userContext = null;
        this.container = null;
    }
    
    /**
     * Initialize the user context display
     */
    async initialize(containerId = 'userContextPanel') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn('User context display container not found:', containerId);
            return;
        }
        
        // Get user context
        this.userContext = await this.getUserContext();
        
        if (this.userContext) {
            this.render();
        } else {
            this.renderUnauthenticated();
        }
    }
    
    /**
     * Get user context from server
     */
    async getUserContext() {
        try {
            const response = await fetch('/api/auth/check-auth', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.user_context || data;
            }
            
            return null;
        } catch (error) {
            console.error('Error getting user context:', error);
            return null;
        }
    }
    
    /**
     * Render user context display
     */
    render() {
        if (!this.container || !this.userContext) return;
        
        const userType = this.getUserType();
        const userTypeLabel = this.getUserTypeLabel(userType);
        const userTypeBadgeClass = this.getUserTypeBadgeClass(userType);
        
        this.container.innerHTML = `
            <div class="user-context-panel">
                <div class="user-info">
                    <div class="user-avatar">
                        <img src="${this.userContext.avatar_url || '/static/images/default-avatar.png'}" 
                             alt="User Avatar" class="rounded-circle" width="48" height="48">
                    </div>
                    <div class="user-details">
                        <h6 class="user-name mb-1">${this.userContext.full_name || this.userContext.username}</h6>
                        <span class="user-role badge bg-secondary me-2">${this.userContext.role || 'user'}</span>
                        <span class="user-type-indicator badge bg-${userTypeBadgeClass}">
                            <i class="fas ${this.getUserTypeIcon(userType)}"></i> ${userTypeLabel}
                        </span>
                    </div>
                </div>
                
                <div class="user-permissions mt-3">
                    <h6 class="text-muted mb-2">Permissions</h6>
                    <div class="permission-badges">
                        ${this.renderPermissions()}
                    </div>
                </div>
                
                ${this.renderOrganizationInfo()}
                
                <div class="user-actions mt-3">
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="showUserProfile()">
                        <i class="fas fa-user"></i> Profile
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-2" onclick="showUserSettings()">
                        <i class="fas fa-cog"></i> Settings
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="logout()">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Render permissions badges
     */
    renderPermissions() {
        if (!this.userContext.permissions || !Array.isArray(this.userContext.permissions)) {
            return '<span class="badge bg-light text-dark">No permissions</span>';
        }
        
        return this.userContext.permissions.map(permission => 
            `<span class="badge bg-primary me-1">${permission}</span>`
        ).join('');
    }
    
    /**
     * Render organization information
     */
    renderOrganizationInfo() {
        if (this.userContext.organization_id) {
            return `
                <div class="user-organization-info mt-3">
                    <h6 class="text-muted mb-2">Organization</h6>
                    <p class="organization-name mb-1">
                        <i class="fas fa-building me-2"></i>
                        ${this.userContext.organization_name || 'Unknown Organization'}
                    </p>
                    <p class="organization-plan text-muted small">
                        <i class="fas fa-info-circle me-1"></i>
                        Organization Plan
                    </p>
                </div>
            `;
        } else {
            return `
                <div class="user-independent-info mt-3">
                    <h6 class="text-muted mb-2">Independent User</h6>
                    <p class="independent-limits text-muted small">
                        <i class="fas fa-info-circle me-2"></i>
                        Personal storage: 5GB | Projects: Unlimited
                    </p>
                </div>
            `;
        }
    }
    
    /**
     * Render unauthenticated state
     */
    renderUnauthenticated() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="user-context-panel">
                <div class="text-center">
                    <div class="user-avatar mb-3">
                        <i class="fas fa-user-circle fa-3x text-muted"></i>
                    </div>
                    <h6 class="text-muted">Not Authenticated</h6>
                    <p class="text-muted small">Please log in to access your account</p>
                    <div class="user-actions">
                        <a href="/api/auth/" class="btn btn-primary btn-sm me-2">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </a>
                        <a href="/api/auth/" class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-user-plus"></i> Sign Up
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Get user type
     */
    getUserType() {
        if (!this.userContext) return 'independent';
        
        if (this.userContext.role === 'super_admin') {
            return 'super_admin';
        } else if (this.userContext.is_independent || !this.userContext.organization_id) {
            return 'independent';
        } else {
            return 'organization_member';
        }
    }
    
    /**
     * Get user type label
     */
    getUserTypeLabel(userType) {
        const labels = {
            'independent': 'Independent User',
            'organization_member': 'Organization Member',
            'super_admin': 'Super Administrator'
        };
        return labels[userType] || 'User';
    }
    
    /**
     * Get user type badge class
     */
    getUserTypeBadgeClass(userType) {
        const badgeClasses = {
            'independent': 'warning',
            'organization_member': 'primary',
            'super_admin': 'danger'
        };
        return badgeClasses[userType] || 'secondary';
    }
    
    /**
     * Get user type icon
     */
    getUserTypeIcon(userType) {
        const icons = {
            'independent': 'fa-user',
            'organization_member': 'fa-users',
            'super_admin': 'fa-crown'
        };
        return icons[userType] || 'fa-user';
    }
    
    /**
     * Update user context display
     */
    async update() {
        this.userContext = await this.getUserContext();
        this.render();
    }
    
    /**
     * Show user profile modal
     */
    showUserProfile() {
        // This would open a user profile modal
        console.log('Show user profile');
        // You could implement a modal here or redirect to profile page
        window.location.href = '/api/auth/profile';
    }
    
    /**
     * Show user settings modal
     */
    showUserSettings() {
        // This would open a user settings modal
        console.log('Show user settings');
        // You could implement a modal here or redirect to settings page
        window.location.href = '/api/auth/settings';
    }
    
    /**
     * Logout user
     */
    async logout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            
            if (response.ok) {
                // Redirect to login page
                window.location.href = '/api/auth/';
            } else {
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }
}

// Export for use in other modules
window.UserContextDisplay = UserContextDisplay;

