/**
 * Authentication Module - Clean Entry Point
 * @description Simple, predictable initialization for the new modular auth system
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/index
 */

console.log('🚀 New Auth Module Loading - Clean Architecture');

// Import all modules
import AuthManager from './auth-state/auth-manager.js';
import SessionManager from './auth-state/session-manager.js';
import AuthAPI from './auth-services/auth-api.js';
import Validation from './auth-services/validation.js';
import Permissions from './auth-services/permissions.js';
import AuthUIManager from './auth-ui/auth-ui-manager.js';
import AuthComponents from './auth-ui/auth-components.js';
import LoginForm from './auth-forms/login-form.js';
import SignupForm from './auth-forms/signup-form.js';
import ProfileForm from './auth-forms/profile-form.js';
import PostLoginOrchestrator from './auth-management/post-login-orchestrator.js';

// Import the business logic from core.js
import { AuthSystemManager } from './auth-management/core.js';

// Make all modules available globally for core.js to use
window.AuthManager = AuthManager;
window.SessionManager = SessionManager;
window.AuthAPI = AuthAPI;
window.Validation = Validation;
window.Permissions = Permissions;
window.AuthUIManager = AuthUIManager;
window.AuthComponents = AuthComponents;
window.LoginForm = LoginForm;
window.SignupForm = SignupForm;
window.ProfileForm = ProfileForm;
window.PostLoginOrchestrator = PostLoginOrchestrator;

// Create and initialize the auth system
const authSystem = AuthSystemManager.createDefault();

/**
 * Initialize the authentication system
 * @description Main initialization function - called when DOM is ready
 */
async function initializeAuth() {
    try {
        await authSystem.initialize();
        console.log('🎉 Auth system ready!');
    } catch (error) {
        console.error('❌ Auth system initialization failed:', error);
        // Don't crash the page - auth is optional
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAuth);
} else {
    initializeAuth();
}

// Export for testing and external use
export { initializeAuth, authSystem, AuthSystemManager };
