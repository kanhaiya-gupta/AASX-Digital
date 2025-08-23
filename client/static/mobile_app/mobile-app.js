/**
 * AASX Digital Twin Analytics - Mobile App
 * Progressive Web App with mobile-optimized interface
 * Integrates with existing FastAPI backend
 */

class AASXMobileApp {
    constructor() {
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.currentUser = null;
        this.authToken = null;
        this.mobileMenuOpen = false;
        
        // Mobile-specific settings
        this.mobileConfig = {
            touchThreshold: 10,
            swipeThreshold: 50,
            animationDuration: 300,
            breakpoint: 768
        };
        
        this.init();
    }

    async init() {
        console.log('📱 AASX Mobile App: Initializing...');
        
        try {
            // Wait for central auth system
            await this.waitForAuthSystem();
            
            // Initialize mobile features
            this.setupMobileFeatures();
            this.setupPWAFeatures();
            this.setupTouchGestures();
            this.setupMobileNavigation();
            this.setupOfflineSupport();
            
            // Initialize mobile UI
            this.initializeMobileUI();
            
            console.log('✅ AASX Mobile App: Initialized successfully');
        } catch (error) {
            console.error('❌ AASX Mobile App: Initialization failed:', error);
        }
    }

    async waitForAuthSystem() {
        return new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                console.log('🔐 Mobile App: Auth system ready');
                this.updateAuthState();
                resolve();
            } else {
                console.log('🔐 Mobile App: Waiting for auth system...');
                const handleReady = () => {
                    console.log('🔐 Mobile App: Auth system ready');
                    window.removeEventListener('authSystemReady', handleReady);
                    this.updateAuthState();
                    resolve();
                };
                window.addEventListener('authSystemReady', handleReady);
            }
        });
    }

    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated;
            this.currentUser = window.authManager.currentUser;
            this.authToken = window.authManager.authToken;
            
            // Update mobile UI based on auth state
            this.updateMobileUI();
        }
    }

    setupMobileFeatures() {
        // Mobile viewport setup
        this.setupViewport();
        
        // Touch event handling
        this.setupTouchEvents();
        
        // Mobile-specific CSS
        this.injectMobileStyles();
        
        // Responsive breakpoint detection
        this.setupResponsiveDetection();
    }

    setupViewport() {
        // Ensure proper mobile viewport
        const viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            const meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
            document.head.appendChild(meta);
        }
    }

    setupTouchEvents() {
        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (event) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);

        // Add touch feedback
        document.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('mobile-button') || 
                e.target.closest('.mobile-button')) {
                e.target.classList.add('touch-active');
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('mobile-button') || 
                e.target.closest('.mobile-button')) {
                setTimeout(() => {
                    e.target.classList.remove('touch-active');
                }, 150);
            }
        });
    }

    setupPWAFeatures() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/mobile_app/pwa/sw.js')
                .then(registration => {
                    console.log('📱 Service Worker registered:', registration);
                    this.setupPWAInstallPrompt();
                })
                .catch(error => {
                    console.error('❌ Service Worker registration failed:', error);
                });
        }

        // PWA install prompt
        this.setupPWAInstallPrompt();
        
        // PWA lifecycle events
        this.setupPWALifecycle();
    }

    setupPWAInstallPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            this.showInstallPrompt();
        });

        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallPrompt();
            console.log('📱 PWA installed successfully');
        });
    }

    showInstallPrompt() {
        // Create install prompt UI
        const installPrompt = document.createElement('div');
        installPrompt.id = 'mobile-install-prompt';
        installPrompt.className = 'mobile-install-prompt';
        installPrompt.innerHTML = `
            <div class="install-content">
                <div class="install-icon">📱</div>
                <div class="install-text">
                    <h3>Install AASX Digital</h3>
                    <p>Add to home screen for quick access</p>
                </div>
                <button class="install-button" onclick="mobileApp.installPWA()">Install</button>
                <button class="install-close" onclick="mobileApp.hideInstallPrompt()">×</button>
            </div>
        `;
        
        document.body.appendChild(installPrompt);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.hideInstallPrompt();
        }, 10000);
    }

    hideInstallPrompt() {
        const prompt = document.getElementById('mobile-install-prompt');
        if (prompt) {
            prompt.remove();
        }
    }

    async installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            console.log('📱 Install prompt outcome:', outcome);
            this.deferredPrompt = null;
        }
    }

    setupTouchGestures() {
        // Swipe navigation
        this.setupSwipeNavigation();
        
        // Pull to refresh
        this.setupPullToRefresh();
        
        // Long press actions
        this.setupLongPress();
    }

    setupSwipeNavigation() {
        let startX, startY, endX, endY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.mobileConfig.swipeThreshold) {
                if (deltaX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
        });
    }

    handleSwipeRight() {
        // Open mobile menu
        this.toggleMobileMenu(true);
    }

    handleSwipeLeft() {
        // Close mobile menu
        this.toggleMobileMenu(false);
    }

    setupMobileNavigation() {
        // Create mobile navigation
        this.createMobileNavigation();
        
        // Setup mobile menu
        this.setupMobileMenu();
        
        // Setup bottom navigation
        this.setupBottomNavigation();
    }

    createMobileNavigation() {
        const nav = document.createElement('nav');
        nav.className = 'mobile-navigation';
        nav.innerHTML = `
            <div class="mobile-nav-header">
                <button class="mobile-menu-toggle" onclick="mobileApp.toggleMobileMenu()">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <div class="mobile-nav-title">AASX Digital</div>
                <button class="mobile-nav-action" onclick="mobileApp.showMobileActions()">
                    ⋯
                </button>
            </div>
            <div class="mobile-nav-menu">
                <div class="mobile-nav-user">
                    <div class="user-avatar">👤</div>
                    <div class="user-info">
                        <div class="user-name">${this.currentUser?.name || 'Guest'}</div>
                        <div class="user-status">${this.isAuthenticated ? 'Authenticated' : 'Demo Mode'}</div>
                    </div>
                </div>
                <div class="mobile-nav-links">
                    <a href="/dashboard" class="mobile-nav-link">
                        <span class="nav-icon">📊</span>
                        <span class="nav-text">Dashboard</span>
                    </a>
                    <a href="/twin-registry" class="mobile-nav-link">
                        <span class="nav-icon">🏗️</span>
                        <span class="nav-text">Twin Registry</span>
                    </a>
                    <a href="/ai-rag" class="mobile-nav-link">
                        <span class="nav-icon">🤖</span>
                        <span class="nav-text">AI/RAG</span>
                    </a>
                    <a href="/certificates" class="mobile-nav-link">
                        <span class="nav-icon">📜</span>
                        <span class="nav-text">Certificates</span>
                    </a>
                    <a href="/federated-learning" class="mobile-nav-link">
                        <span class="nav-icon">🔗</span>
                        <span class="nav-text">Federated Learning</span>
                    </a>
                    <a href="/physics-modeling" class="mobile-nav-link">
                        <span class="nav-icon">⚛️</span>
                        <span class="nav-text">Physics Modeling</span>
                    </a>
                </div>
            </div>
        `;
        
        document.body.insertBefore(nav, document.body.firstChild);
    }

    toggleMobileMenu(force = null) {
        const menu = document.querySelector('.mobile-nav-menu');
        const toggle = document.querySelector('.mobile-menu-toggle');
        
        if (force !== null) {
            this.mobileMenuOpen = force;
        } else {
            this.mobileMenuOpen = !this.mobileMenuOpen;
        }
        
        if (this.mobileMenuOpen) {
            menu.classList.add('open');
            toggle.classList.add('active');
            document.body.classList.add('menu-open');
        } else {
            menu.classList.remove('open');
            toggle.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    }

    setupBottomNavigation() {
        const bottomNav = document.createElement('nav');
        bottomNav.className = 'mobile-bottom-nav';
        bottomNav.innerHTML = `
            <a href="/dashboard" class="bottom-nav-item">
                <span class="bottom-nav-icon">📊</span>
                <span class="bottom-nav-text">Dashboard</span>
            </a>
            <a href="/twin-registry" class="bottom-nav-item">
                <span class="bottom-nav-icon">🏗️</span>
                <span class="bottom-nav-text">Twins</span>
            </a>
            <a href="/ai-rag" class="bottom-nav-item">
                <span class="bottom-nav-icon">🤖</span>
                <span class="bottom-nav-text">AI</span>
            </a>
            <a href="/certificates" class="bottom-nav-item">
                <span class="bottom-nav-icon">📜</span>
                <span class="bottom-nav-text">Certs</span>
            </a>
            <a href="/physics-modeling" class="bottom-nav-item">
                <span class="bottom-nav-icon">⚛️</span>
                <span class="bottom-nav-text">Physics</span>
            </a>
        `;
        
        document.body.appendChild(bottomNav);
    }

    setupOfflineSupport() {
        // Online/offline detection
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showOnlineStatus();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineStatus();
        });
    }

    showOnlineStatus() {
        this.showMobileToast('🟢 Back online', 'success');
    }

    showOfflineStatus() {
        this.showMobileToast('🔴 You are offline', 'warning');
    }

    showMobileToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `mobile-toast mobile-toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    injectMobileStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Mobile App Styles */
            .mobile-navigation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 60px;
                background: #2563eb;
                color: white;
                z-index: 1000;
                display: flex;
                align-items: center;
                padding: 0 16px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .mobile-nav-header {
                display: flex;
                align-items: center;
                width: 100%;
            }

            .mobile-menu-toggle {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 8px;
                margin-right: 16px;
            }

            .mobile-menu-toggle span {
                display: block;
                width: 24px;
                height: 2px;
                background: white;
                margin: 4px 0;
                transition: 0.3s;
            }

            .mobile-menu-toggle.active span:nth-child(1) {
                transform: rotate(45deg) translate(5px, 5px);
            }

            .mobile-menu-toggle.active span:nth-child(2) {
                opacity: 0;
            }

            .mobile-menu-toggle.active span:nth-child(3) {
                transform: rotate(-45deg) translate(7px, -6px);
            }

            .mobile-nav-title {
                flex: 1;
                font-size: 18px;
                font-weight: 600;
            }

            .mobile-nav-action {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 8px;
            }

            .mobile-nav-menu {
                position: fixed;
                top: 60px;
                left: -280px;
                width: 280px;
                height: calc(100vh - 60px);
                background: white;
                box-shadow: 2px 0 8px rgba(0,0,0,0.1);
                transition: left 0.3s ease;
                z-index: 999;
                overflow-y: auto;
            }

            .mobile-nav-menu.open {
                left: 0;
            }

            .mobile-nav-user {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                align-items: center;
            }

            .user-avatar {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: #2563eb;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-right: 12px;
            }

            .user-name {
                font-weight: 600;
                font-size: 16px;
            }

            .user-status {
                font-size: 12px;
                color: #6b7280;
            }

            .mobile-nav-links {
                padding: 16px 0;
            }

            .mobile-nav-link {
                display: flex;
                align-items: center;
                padding: 16px 20px;
                color: #374151;
                text-decoration: none;
                transition: background 0.2s;
            }

            .mobile-nav-link:hover {
                background: #f3f4f6;
            }

            .nav-icon {
                font-size: 20px;
                margin-right: 12px;
                width: 24px;
                text-align: center;
            }

            .nav-text {
                font-size: 16px;
            }

            .mobile-bottom-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 60px;
                background: white;
                border-top: 1px solid #e5e7eb;
                display: flex;
                z-index: 1000;
            }

            .bottom-nav-item {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #6b7280;
                text-decoration: none;
                font-size: 12px;
                transition: color 0.2s;
            }

            .bottom-nav-item:hover,
            .bottom-nav-item.active {
                color: #2563eb;
            }

            .bottom-nav-icon {
                font-size: 20px;
                margin-bottom: 4px;
            }

            .mobile-install-prompt {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2000;
            }

            .install-content {
                background: white;
                border-radius: 12px;
                padding: 24px;
                margin: 20px;
                max-width: 320px;
                text-align: center;
            }

            .install-icon {
                font-size: 48px;
                margin-bottom: 16px;
            }

            .install-text h3 {
                margin: 0 0 8px 0;
                font-size: 18px;
            }

            .install-text p {
                margin: 0 0 20px 0;
                color: #6b7280;
            }

            .install-button {
                background: #2563eb;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                margin-right: 8px;
            }

            .install-close {
                background: #e5e7eb;
                color: #374151;
                border: none;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
            }

            .mobile-toast {
                position: fixed;
                top: 80px;
                left: 50%;
                transform: translateX(-50%) translateY(-100px);
                background: #374151;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                z-index: 2000;
                transition: transform 0.3s ease;
            }

            .mobile-toast.show {
                transform: translateX(-50%) translateY(0);
            }

            .mobile-toast-success {
                background: #059669;
            }

            .mobile-toast-warning {
                background: #d97706;
            }

            .mobile-toast-error {
                background: #dc2626;
            }

            /* Mobile responsive adjustments */
            @media (max-width: 768px) {
                body {
                    padding-top: 60px;
                    padding-bottom: 60px;
                }

                .mobile-button {
                    min-height: 44px;
                    padding: 12px 16px;
                    font-size: 16px;
                    border-radius: 8px;
                    transition: all 0.2s;
                }

                .mobile-button.touch-active {
                    transform: scale(0.95);
                    opacity: 0.8;
                }

                .menu-open {
                    overflow: hidden;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    setupResponsiveDetection() {
        const checkMobile = () => {
            const isMobile = window.innerWidth <= this.mobileConfig.breakpoint;
            document.body.classList.toggle('mobile-view', isMobile);
        };
        
        checkMobile();
        window.addEventListener('resize', checkMobile);
    }

    initializeMobileUI() {
        // Add mobile-specific classes
        document.body.classList.add('mobile-app');
        
        // Initialize mobile components
        this.initializeMobileComponents();
        
        // Setup mobile-specific event listeners
        this.setupMobileEventListeners();
    }

    initializeMobileComponents() {
        // Convert existing buttons to mobile-friendly
        this.convertButtonsToMobile();
        
        // Add mobile-specific loading states
        this.addMobileLoadingStates();
        
        // Setup mobile forms
        this.setupMobileForms();
    }

    convertButtonsToMobile() {
        const buttons = document.querySelectorAll('button, .btn, input[type="submit"]');
        buttons.forEach(button => {
            button.classList.add('mobile-button');
        });
    }

    addMobileLoadingStates() {
        // Add mobile loading spinner
        const loadingSpinner = document.createElement('div');
        loadingSpinner.id = 'mobile-loading';
        loadingSpinner.className = 'mobile-loading';
        loadingSpinner.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading...</div>
        `;
        document.body.appendChild(loadingSpinner);
    }

    setupMobileForms() {
        // Only target forms that are specifically for mobile functionality
        const mobileForms = document.querySelectorAll('form.mobile-form, .mobile-section form, [data-mobile="true"] form');
        mobileForms.forEach(form => {
            form.classList.add('mobile-form');
            
            // Add mobile-specific form handling
            form.addEventListener('submit', (e) => {
                console.log('📱 Mobile App: Handling mobile form submission');
                this.showMobileLoading();
            });
        });
        
        console.log(`📱 Mobile App: Setup ${mobileForms.length} mobile forms`);
    }

    showMobileLoading() {
        const loading = document.getElementById('mobile-loading');
        if (loading) {
            loading.classList.add('show');
        }
    }

    hideMobileLoading() {
        const loading = document.getElementById('mobile-loading');
        if (loading) {
            loading.classList.remove('show');
        }
    }

    setupMobileEventListeners() {
        // Handle mobile-specific interactions
        document.addEventListener('click', (e) => {
            // Add touch feedback
            if (e.target.classList.contains('mobile-button')) {
                this.addTouchFeedback(e.target);
            }
        });

        // Handle mobile navigation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.mobile-nav-link')) {
                this.toggleMobileMenu(false);
            }
        });
    }

    addTouchFeedback(element) {
        element.classList.add('touch-active');
        setTimeout(() => {
            element.classList.remove('touch-active');
        }, 150);
    }

    updateMobileUI() {
        // Update UI based on authentication state
        const userInfo = document.querySelector('.user-name');
        const userStatus = document.querySelector('.user-status');
        
        if (userInfo && userStatus) {
            userInfo.textContent = this.currentUser?.name || 'Guest';
            userStatus.textContent = this.isAuthenticated ? 'Authenticated' : 'Demo Mode';
        }
    }

    // Public API methods
    showMobileActions() {
        // Show mobile action sheet
        this.showMobileToast('Action menu coming soon', 'info');
    }

    setupPWALifecycle() {
        // Handle PWA lifecycle events
        window.addEventListener('load', () => {
            console.log('📱 PWA loaded');
        });

        window.addEventListener('focus', () => {
            console.log('📱 PWA focused');
        });

        window.addEventListener('blur', () => {
            console.log('📱 PWA blurred');
        });
    }
}

// Initialize mobile app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new AASXMobileApp();
});

// Export for global access
window.AASXMobileApp = AASXMobileApp;
