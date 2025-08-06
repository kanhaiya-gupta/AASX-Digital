/**
 * Navigation Management Component
 * Handles navigation highlighting and navigation-related functionality
 */

export class NavigationManager {
    constructor() {
        this.isInitialized = false;
        this.currentModule = 'home';
    }

    /**
     * Initialize navigation management
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🧭 Initializing Navigation Manager...');
        
        try {
            // Set up navigation highlighting
            this.highlightCurrentNav();
            
            // Set up navigation event listeners
            this.setupNavigationListeners();
            
            this.isInitialized = true;
            console.log('✅ Navigation Manager initialized');
            
        } catch (error) {
            console.error('❌ Navigation Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Highlight current navigation item
     */
    highlightCurrentNav() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Setup navigation event listeners
     */
    setupNavigationListeners() {
        // Handle navigation clicks
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                this.handleNavigationClick(e);
            });
        });
    }

    /**
     * Handle navigation click
     */
    handleNavigationClick(event) {
        const link = event.currentTarget;
        const href = link.getAttribute('href');
        
        // Update current module
        this.updateCurrentModule(href);
        
        // Highlight clicked link
        this.highlightNavLink(link);
    }

    /**
     * Update current module
     */
    updateCurrentModule(path) {
        if (path === '/') {
            this.currentModule = 'home';
        } else if (path.includes('/auth')) {
            this.currentModule = 'auth';
        } else if (path.includes('/aasx-etl')) {
            this.currentModule = 'aasx-etl';
        } else if (path.includes('/twin-registry')) {
            this.currentModule = 'twin-registry';
        } else if (path.includes('/ai-rag')) {
            this.currentModule = 'ai-rag';
        } else if (path.includes('/kg-neo4j')) {
            this.currentModule = 'kg-neo4j';
        } else if (path.includes('/certificate-manager')) {
            this.currentModule = 'certificate-manager';
        } else if (path.includes('/federated-learning')) {
            this.currentModule = 'federated-learning';
        } else if (path.includes('/physics-modeling')) {
            this.currentModule = 'physics-modeling';
        }
        
        // Dispatch module change event
        window.dispatchEvent(new CustomEvent('moduleChanged', {
            detail: { module: this.currentModule }
        }));
    }

    /**
     * Highlight navigation link
     */
    highlightNavLink(link) {
        // Remove active class from all links
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(navLink => {
            navLink.classList.remove('active');
        });
        
        // Add active class to clicked link
        link.classList.add('active');
    }

    /**
     * Get current module
     */
    getCurrentModule() {
        return this.currentModule;
    }

    /**
     * Navigate to module
     */
    navigateToModule(module) {
        const modulePaths = {
            'home': '/',
            'auth': '/auth',
            'aasx-etl': '/aasx-etl',
            'twin-registry': '/twin-registry',
            'ai-rag': '/ai-rag',
            'kg-neo4j': '/kg-neo4j',
            'certificate-manager': '/certificate-manager',
            'federated-learning': '/federated-learning',
            'physics-modeling': '/physics-modeling'
        };
        
        const path = modulePaths[module];
        if (path) {
            window.location.href = path;
        }
    }

    /**
     * Cleanup navigation manager
     */
    destroy() {
        this.isInitialized = false;
        console.log('🧹 Navigation Manager destroyed');
    }
} 