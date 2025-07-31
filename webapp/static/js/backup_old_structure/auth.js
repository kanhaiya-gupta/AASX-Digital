/**
 * Authentication Management Script
 * Handles user authentication, session management, and UI updates
 */

// Authentication state management
let currentUser = null;
let isAuthenticated = false;

/**
 * Check authentication status on page load
 */
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/check-auth');
        const result = await response.json();
        
        if (result.authenticated) {
            isAuthenticated = true;
            currentUser = result.user;
            showAuthenticatedUI();
        } else {
            showUnauthenticatedUI();
        }
    } catch (error) {
        console.log('Auth check failed:', error);
        showUnauthenticatedUI();
    }
}

/**
 * Show authenticated user interface
 */
function showAuthenticatedUI() {
    const unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
    const authenticatedMenu = document.getElementById('authenticatedMenu');
    const userDisplayName = document.getElementById('userDisplayName');
    const adminUsersLink = document.getElementById('adminUsersLink');
    const welcomeSection = document.getElementById('welcomeSection');
    const welcomeUserName = document.getElementById('welcomeUserName');
    const welcomeUserRole = document.getElementById('welcomeUserRole');
    const adminLink = document.getElementById('adminLink');
    
    // Update User tab dropdown
    if (unauthenticatedMenu && authenticatedMenu) {
        unauthenticatedMenu.style.display = 'none';
        authenticatedMenu.style.display = 'block';
        
        // Set user display name
        if (userDisplayName && currentUser) {
            userDisplayName.textContent = currentUser.full_name || currentUser.username;
        }
        
        // Show admin link if user is admin
        if (adminUsersLink && currentUser && currentUser.role === 'admin') {
            adminUsersLink.style.display = 'block';
            adminUsersLink.href = '/auth/admin/users';
        }
    }
    
    // Update welcome section on dashboard
    if (welcomeSection && currentUser) {
        welcomeSection.style.display = 'block';
        
        if (welcomeUserName) {
            welcomeUserName.textContent = currentUser.full_name || currentUser.username;
        }
        
        if (welcomeUserRole) {
            welcomeUserRole.textContent = currentUser.role;
        }
        
        if (adminLink && currentUser.role === 'admin') {
            adminLink.style.display = 'inline-block';
        }
    }
}

/**
 * Show unauthenticated user interface
 */
function showUnauthenticatedUI() {
    const unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
    const authenticatedMenu = document.getElementById('authenticatedMenu');
    const welcomeSection = document.getElementById('welcomeSection');
    
    if (unauthenticatedMenu && authenticatedMenu) {
        unauthenticatedMenu.style.display = 'block';
        authenticatedMenu.style.display = 'none';
    }
    
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
}

/**
 * Logout function
 */
async function logout() {
    try {
        const response = await fetch('/auth/api/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Reset authentication state
            isAuthenticated = false;
            currentUser = null;
            showUnauthenticatedUI();
            
            // Show success message
            showNotification('Logged out successfully', 'success');
            
            // Redirect to login page after a short delay
            setTimeout(() => {
                window.location.href = '/auth/login';
            }, 1000);
        } else {
            console.error('Logout failed');
            showNotification('Logout failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Logout error. Please try again.', 'error');
        // Still redirect to login page even if logout fails
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Prevent infinite recursion
    if (window.showNotification && window.showNotification !== showNotification) {
        window.showNotification(message, type);
    } else {
        alert(message);
    }
}

/**
 * Initialize authentication on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
});

/**
 * Add authentication check to protected pages
 */
function requireAuth() {
    if (!isAuthenticated) {
        showNotification('Please log in to access this page', 'warning');
        window.location.href = '/auth/login';
        return false;
    }
    return true;
}

/**
 * Add admin check
 */
function requireAdmin() {
    if (!requireAuth()) return false;
    if (!currentUser || currentUser.role !== 'admin') {
        showNotification('Admin access required', 'error');
        window.location.href = '/';
        return false;
    }
    return true;
}

/**
 * Get current user information
 */
function getCurrentUser() {
    return currentUser;
}

/**
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    return isAuthenticated;
}

/**
 * Check if user is admin
 */
function isUserAdmin() {
    return isAuthenticated && currentUser && currentUser.role === 'admin';
}

// Export functions for use in other scripts
window.auth = {
    checkAuthStatus,
    showAuthenticatedUI,
    showUnauthenticatedUI,
    logout,
    requireAuth,
    requireAdmin,
    getCurrentUser,
    isUserAuthenticated,
    isUserAdmin
}; 