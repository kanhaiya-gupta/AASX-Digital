/**
 * AASX Data Manager Core
 * Main DataManager class for managing data, use cases, and projects
 */

import { formatFileSize, getFileStatusInfo, getStatusBadgeColor } from '/static/js/shared/utils.js';
import { showSuccess, showError, showWarning } from '/static/js/shared/alerts.js';

export class DataManager {
    constructor() {
        this.isInitialized = false;
        this.isProcessing = false;
        this.isViewingProjects = false; // Flag to track if user is viewing projects
        this.projects = [];
        this.useCases = [];
        this.currentProject = null;
        this.currentUseCase = null;
        this.currentFile = null;
        this.fileList = [];
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
        
        // Initialize other components
        this.initComponents();
    }

    /**
     * Initialize components
     */
    initComponents() {
        // Initialize any additional components here
        console.log('🔧 Data Manager: Components initialized');
    }

    





    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        // Get token from global auth manager
        const token = this.getStoredToken();
        
        if (!token) {
            console.log('🔐 No auth token available - making unauthenticated request');
            return {};
        }
        
        console.log('🔐 Auth token available - making authenticated request');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Wait for global auth manager to be ready
     */
    async waitForAuthManager() {
        console.log('🔐 Data Manager: Waiting for global auth manager...');
        
        // CRITICAL FIX: Wait for auth system to be completely ready
        // This ensures we get the most up-to-date auth manager instance
        if (!window.authManager || !window.authSystemReady) {
            console.log('⏳ Data Manager: Waiting for auth system to be completely ready...');
            await new Promise(resolve => {
                const handleAuthSystemReady = (event) => {
                    console.log('🚀 Data Manager: Auth system ready event received');
                    window.removeEventListener('authSystemReady', handleAuthSystemReady);
                    resolve();
                };
                
                // Listen for auth system ready event
                window.addEventListener('authSystemReady', handleAuthSystemReady);
                
                // Fallback: also check for both conditions periodically
                const checkInterval = setInterval(() => {
                    if (window.authManager && window.authSystemReady) {
                        clearInterval(checkInterval);
                        window.removeEventListener('authSystemReady', handleAuthSystemReady);
                        resolve();
                    }
                }, 100);
                
                // Timeout after 10 seconds
                setTimeout(() => {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleAuthSystemReady);
                    console.warn('⚠️ Data Manager: Timeout waiting for auth system');
                    resolve();
                }, 10000);
            });
        }
        
        // Final check: ensure auth manager is available
        while (!window.authManager) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Data Manager: Global auth manager ready');
        
        // Initial auth state setup
        this.updateAuthState();
        
        // Listen for auth changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Data Manager: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        // 🚫 CRITICAL FIX: Remove duplicate loginSuccess listener - PostLoginOrchestrator handles this
        // window.addEventListener('loginSuccess', async () => {
        //     console.log('🔐 Data Manager: Login success detected');
        //     this.updateAuthState();
        //     
        //     // 🚀 WORLD-CLASS: Immediately refresh user data after login
        //     console.log('🔄 Data Manager: Refreshing user data after login...');
        //         try {
        //             await this.loadProjects();
        //             console.log('✅ Data Manager: User data refreshed successfully after login');
        //             await this.loadUseCases();
        //             console.log('✅ Data Manager: Use cases refreshed successfully after login');
        //         } catch (error) {
        //             console.error('❌ Data Manager: Failed to refresh user data after login:', error);
        //         }
        // });
        
        window.addEventListener('logout', () => {
            console.log('🔐 Data Manager: Logout detected');
            this.updateAuthState();
        });
    }

    /**
     * Update authentication state from global auth manager
     */
    updateAuthState() {
        // CRITICAL FIX: Check if new auth system is ready and take precedence
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Data Manager: Using new auth system');
        } else if (window.authManager) {
            console.log('🔐 Data Manager: Using fallback auth manager');
        } else {
            console.log('⚠️ Data Manager: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 Data Manager: Auth state update:', sessionInfo);
            
            // Store previous user for comparison
            const previousUser = this.currentUser?.username;
            
            // Update local state based on global auth manager
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            
            // Update UI based on auth state
            this.updateUIForAuthState();
            
            // 🚫 CRITICAL FIX: Reload user data when auth state changes
            // This ensures demo data is replaced with real user data
            if (this.isAuthenticated && this.currentUser && 
                previousUser !== this.currentUser.username) {
                console.log('🔄 Data Manager: User changed, reloading data...');
                this.reloadUserData();
            }
            
        } catch (error) {
            console.warn('⚠️ Data Manager: Error updating auth state:', error);
        }
    }

    /**
     * Update UI based on current authentication state
     */
    updateUIForAuthState() {
        if (this.isAuthenticated && this.currentUser) {
            console.log('🔐 Data Manager: User authenticated:', this.currentUser.username);
            // User is authenticated - UI will show their data
        } else {
            console.log('🔐 Data Manager: User not authenticated (demo mode)');
            // User is not authenticated - UI will show demo data
        }
    }

    /**
     * Reload user data when authentication state changes
     * This ensures demo data is replaced with real user data
     */
    async reloadUserData() {
        try {
            console.log('🔄 Data Manager: Reloading user data after auth change...');
            
            // Clear existing data first
            this.projects = [];
            this.useCases = [];
            
            // 🚫 CRITICAL FIX: Clear cache to force fresh data loading
            this._groupedUseCasesCache = null;
            
            // 🚫 CRITICAL FIX: loadProjects() actually loads both projects AND use cases
            // The method name is misleading - it loads both via Promise.all
            await this.loadProjects();
            
            console.log('✅ Data Manager: User data reloaded successfully');
            
        } catch (error) {
            console.error('❌ Data Manager: Failed to reload user data:', error);
        }
    }

    /**
     * Show authentication required message for authenticated users
     */
    showAuthenticationRequired() {
        console.log('🔐 Showing authentication required message for authenticated user');
        
        if (typeof showWarning === 'function') {
            showWarning('Your session has expired. Please log in again to access your data.');
        } else {
            console.warn('⚠️ Authentication required - please log in again');
        }
    }

    /**
     * Get stored authentication token
     * @returns {string|null} Stored token or null
     */
    getStoredToken() {
        try {
            // Try to get token from auth manager first
            if (window.authManager && typeof window.authManager.getStoredToken === 'function') {
                return window.authManager.getStoredToken();
            }
            
            // Fallback to localStorage
            return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
        } catch (error) {
            console.warn('⚠️ Could not retrieve stored token:', error);
            return null;
        }
    }

    async init() {
        // 🚫 CRITICAL FIX: Prevent duplicate initialization
        if (this.isInitialized) {
            console.log('⚠️ Data Manager already initialized, skipping...');
            return;
        }
        
        console.log('🚀 Data Manager initializing...');
        
        try {
            // Wait for global auth manager to be ready
            await this.waitForAuthManager();
            
            this.setupEventListeners();
            this.initFlowChart();
            await this.loadProjects();
            this.startAutoRefresh();
            
            this.isInitialized = true;
            console.log('✅ Data Manager initialized successfully');
        } catch (error) {
            console.error('❌ Data Manager initialization failed:', error);
        }
    }

    setupEventListeners() {
        // Back to use cases button
        $(document).on('click', '#backToUseCases', () => {
            this.showUseCasesSimple();
        });

        // Use case click handler
        $(document).on('click', '.use-case-card', (e) => {
            const useCaseId = $(e.currentTarget).data('use-case-id');
            this.selectUseCase(useCaseId);
        });

        // Project view button handler
        $(document).on('click', '.btn-view-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.viewProject(projectId);
        });

        // Project upload button handler
        $(document).on('click', '.btn-upload-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.uploadToProject(projectId);
        });

        // Project delete button handler
        $(document).on('click', '.btn-delete-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.deleteProject(projectId);
        });

        // Refresh data button handler
        $(document).on('click', '#refreshDataBtn', (e) => {
            e.preventDefault();
            console.log('🔄 Refresh Data button clicked');
            this.refreshData();
        });

        console.log('📋 Event listeners setup complete');
    }

    // Initialize flow chart
    initFlowChart() {
        this.addFlowStepTooltips();
        
        // Add click handlers for flow steps
        $('.flow-step').on('click', function() {
            const stepNumber = $(this).index() / 2 + 1;
            const stepActions = {
                1: () => $('#fileUpload').click(),
                2: () => $('#createProject').click(),
                3: () => $('#refreshFiles').click(),
                4: () => $('.category-card').first().click(),
                5: () => window.location.href = '/aasx/analytics'
            };
            
            if (stepActions[stepNumber]) {
                stepActions[stepNumber]();
            }
        });
        
        // Add cursor pointer to flow steps
        $('.flow-step').css('cursor', 'pointer');
        
        // Initialize Mermaid flowchart
        this.initMermaidFlowchart();
    }

    // Initialize Mermaid flowchart
    initMermaidFlowchart() {
        try {
            // Configure Mermaid
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    },
                    themeVariables: {
                        primaryColor: '#007bff',
                        primaryTextColor: '#ffffff',
                        primaryBorderColor: '#0056b3',
                        lineColor: '#333333',
                        secondaryColor: '#28a745',
                        tertiaryColor: '#ffc107'
                    }
                });
                
                // Render the flowchart
                mermaid.init(undefined, '.mermaid');
                
                console.log('✅ Mermaid flowchart initialized successfully');
            } else {
                console.warn('⚠️ Mermaid not available, using fallback');
                this.showFlowchartFallback();
            }
            
        } catch (error) {
            console.error('❌ Failed to initialize Mermaid flowchart:', error);
            // Fallback: show a simple text representation
            this.showFlowchartFallback();
        }
    }

    // Fallback for when Mermaid fails to load
    showFlowchartFallback() {
        const fallbackHtml = `
            <div class="flowchart-fallback">
                <div class="text-center">
                    <h6 class="text-primary mb-3">Data Management Hierarchy</h6>
                    <div class="hierarchy-tree">
                        <div class="level-1">
                            <div class="node primary">📊 Data Management</div>
                            <div class="arrow">↓</div>
                        </div>
                        <div class="level-2">
                            <div class="node success">🔥 Thermal Analysis</div>
                            <div class="node warning">🏗️ Structural Analysis</div>
                            <div class="node info">💧 Fluid Dynamics</div>
                            <div class="node secondary">🔗 Multi-Physics</div>
                            <div class="node dark">🏭 Industrial Applications</div>
                        </div>
                        <div class="arrow">↓</div>
                        <div class="level-3">
                            <div class="node light">📁 Projects</div>
                        </div>
                        <div class="arrow">↓</div>
                        <div class="level-4">
                            <div class="node light">📄 AASX Files</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('.mermaid').html(fallbackHtml);
    }

    // Add tooltips to flow steps
    addFlowStepTooltips() {
        $('.flow-step').each(function() {
            const stepNumber = $(this).index() / 2 + 1;
            const tooltips = {
                1: 'Upload AASX files to get started',
                2: 'Create a new project to organize your files',
                3: 'Refresh to see your uploaded files',
                4: () => $('.category-card').first().attr('title'), // Tooltip for category card
                5: 'View analytics and insights'
            };
            
            if (tooltips[stepNumber]) {
                $(this).attr('title', tooltips[stepNumber]);
            }
        });
    }

    // Refresh all data
    async refreshData() {
        console.log('🔄 Refreshing all data...');
        try {
            await this.loadProjects();
            showSuccess('Data refreshed successfully');
        } catch (error) {
            console.error('❌ Error refreshing data:', error);
            showError('Failed to refresh data');
        }
    }

    async loadProjects() {
        console.log('🔄 Loading projects and use cases...');
        console.log(`🔐 Current auth state: ${this.isAuthenticated ? 'Authenticated' : 'Demo mode'}`);
        
        try {
            // Load both projects and use cases with authentication
            const [projectsResponse, useCasesResponse] = await Promise.all([
                fetch('/api/aasx-etl/projects', {
                    headers: this.getAuthHeaders()
                }),
                fetch('/api/aasx-etl/use-cases', {
                    headers: this.getAuthHeaders()
                })
            ]);
            
            console.log('📡 Projects response status:', projectsResponse.status);
            console.log('📡 Use cases response status:', useCasesResponse.status);
            
            if (projectsResponse.ok && useCasesResponse.ok) {
                this.projects = await projectsResponse.json();
                this.useCases = await useCasesResponse.json();
                
                console.log('📦 Loaded projects:', this.projects.length);
                console.log('📋 Loaded use cases:', this.useCases.length);
                
                if (this.projects.length > 0) {
                    console.log('🔍 Sample project structure:', this.projects[0]);
                }
                
                // Group projects by use case (now async)
                await this.groupProjectsByUseCase();
                
                // Only show use cases if user is not currently viewing projects
                if (!this.isViewingProjects) {
                    await this.showUseCases();
                }
                
                // Update stats
                await this.updateStats();
                
            } else {
                console.error('❌ API calls failed:', {
                    'Projects API': projectsResponse.status + ' ' + projectsResponse.statusText,
                    'Use Cases API': useCasesResponse.status + ' ' + useCasesResponse.statusText
                });
                
                // Handle different error types appropriately
                if (projectsResponse.status === 401 || useCasesResponse.status === 401) {
                    // Authentication required - this should not happen for demo users
                    console.log('🔐 Authentication required - user needs to login for full access');
                    if (!this.isAuthenticated) {
                        console.log('✅ Demo mode - showing limited data access');
                    } else {
                        this.showAuthenticationRequired();
                    }
                } else if (projectsResponse.status >= 500 || useCasesResponse.status >= 500) {
                    // Server/database error
                    this.showDatabaseError('Failed to load data from database. Please ensure the database is properly initialized.');
                } else {
                    // Other client errors (403, 404, etc.)
                    this.showErrorMessage('Failed to load data. Please check your permissions and try again.');
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showDatabaseError('Database error while loading data');
        }
    }



    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.autoRefresh();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    async autoRefresh() {
        await this.loadProjects();
    }

    async refreshAndSync() {
        try {
            const response = await fetch('/api/aasx-etl/projects/sync', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                showSuccess('Projects synchronized successfully!');
                // 🚫 CRITICAL FIX: Clear cache to force fresh data loading
                this._groupedUseCasesCache = null;
                await this.loadProjects();
            } else {
                showError('Failed to synchronize projects');
            }
        } catch (error) {
            showError(`Sync error: ${error.message}`);
        }
    }

    // Utility methods
    showSuccessMessage(message) {
        if (typeof showSuccess === 'function') {
            showSuccess(message);
        } else {
            console.log('✅', message);
        }
    }

    showErrorMessage(message) {
        if (typeof showError === 'function') {
            showError(message);
        } else {
            console.error('❌', message);
        }
    }

    showWarningMessage(message) {
        if (typeof showWarning === 'function') {
            showWarning(message);
        } else {
            console.warn('⚠️', message);
        }
    }

    // Cleanup method
    destroy() {
        this.stopAutoRefresh();
        this.isInitialized = false;
        console.log('🧹 Project Manager destroyed');
    }

    // Database error handler
    showDatabaseError(message) {
        if (typeof showError === 'function') {
            showError(message);
        } else {
            console.error('❌ Database Error:', message);
        }
    }
    


    // Update stats with fallback values
    async updateStatsWithFallback() {
        console.log('📊 Stats API not available, using fallback values');
        
        const stats = {
            total_projects: 0,
            total_files: 0,
            processed_files: 0,
            success_rate: 0.0,
            last_updated: new Date().toISOString()
        };
        
        // Update UI with fallback stats
        $('#totalProjects').text(stats.total_projects);
        $('#totalFiles').text(stats.total_files);
        $('#processedFiles').text(stats.processed_files);
        $('#successRate').text(stats.success_rate.toFixed(1) + '%');
        
        return stats;
    }

    // Update stats from API
    async updateStats() {
        try {
            // Always use auth headers - the backend will handle authentication
            const headers = this.getAuthHeaders();
            const response = await fetch('/api/aasx-etl/stats', {
                headers: headers
            });
            if (response.ok) {
                const stats = await response.json();
                
                // Update UI
                $('#totalProjects').text(stats.total_projects);
                $('#totalFiles').text(stats.total_files);
                $('#processedFiles').text(stats.processed_files);
                $('#successRate').text(stats.success_rate.toFixed(1) + '%');
                
                return stats;
            } else {
                console.error('Stats API failed:', response.status, response.statusText);
                
                // Handle different error types appropriately
                if (response.status === 401) {
                    // Authentication required
                    if (!this.isAuthenticated) {
                        console.log('🔐 Stats API requires authentication - demo mode, using fallback');
                    } else {
                        console.log('🔐 Stats API requires authentication - user needs to re-authenticate');
                    }
                    return this.updateStatsWithFallback();
                } else if (response.status >= 500) {
                    // Server/database error
                    this.showDatabaseError('Failed to load statistics from database');
                } else {
                    // Other client errors (403, 404, etc.)
                    console.warn('Stats API client error:', response.status, response.statusText);
                }
                
                return this.updateStatsWithFallback();
            }
        } catch (error) {
            console.error('Error updating stats:', error);
            this.showDatabaseError('Database error while loading statistics');
            return this.updateStatsWithFallback();
        }
    }

    // Group projects by category
    groupProjectsByCategory(projects = null) {
        const projectsToGroup = projects || this.projects;
        const categories = {};
        
        projectsToGroup.forEach(project => {
            const category = project.category || 'uncategorized';
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(project);
        });
        
        return categories;
    }

    // Group projects by use case
    async groupProjectsByUseCase() {
        // 🚫 CRITICAL FIX: Prevent duplicate API calls by caching grouped data
        if (this._groupedUseCasesCache && this._groupedUseCasesCache.timestamp > Date.now() - 30000) {
            console.log('📋 Data Manager: Using cached grouped use cases data (cache age: < 30s)');
            console.log('🔍 DEBUG: Cached data structure:', this._groupedUseCasesCache.data.map(uc => ({
                use_case_id: uc.use_case_id,
                name: uc.name,
                hasProjects: 'projects' in uc,
                projectsLength: Array.isArray(uc.projects) ? uc.projects.length : 'not array'
            })));
            
            // ✅ CRITICAL: Update this.useCases with cached data!
            this.useCases = this._groupedUseCasesCache.data;
            return this._groupedUseCasesCache.data;
        }
        
        console.log('🔄 Data Manager: Loading projects for use cases (API call)...');
        const useCasesWithProjects = [];
        
        for (const useCase of this.useCases) {
            try {
                // Load projects for each use case using the same API as dropdown manager
                console.log(`🔍 Data Manager: Loading projects for use case ${useCase.use_case_id} (${useCase.name})`);
                
                // Always use auth headers - the backend will handle authentication
                const headers = this.getAuthHeaders();
                console.log(`🔐 Loading projects for use case ${useCase.name} with auth: ${this.isAuthenticated ? 'Yes' : 'No'}`);
                
                const response = await fetch(`/api/aasx-etl/use-cases/${useCase.use_case_id}/projects`, {
                    headers: headers
                });
                if (response.ok) {
                    const projects = await response.json();
                    console.log(`📁 Data Manager: Raw projects response for ${useCase.name}:`, projects);
                    
                    // Debug: Check file_count for each project
                    projects.forEach(project => {
                        console.log(`🔍 Project ${project.name}: file_count = ${project.file_count}, files array length = ${project.files ? project.files.length : 'no files array'}`);
                    });
                    
                    useCasesWithProjects.push({
                        ...useCase,  // ✅ Preserve ALL original properties
                        projects: projects  // ✅ Add projects array
                    });
                    console.log(`📁 Data Manager: Loaded ${projects.length} projects for use case: ${useCase.name}`);
                    console.log(`📋 Data Manager: Project names:`, projects.map(p => p.name));
                } else {
                    console.warn(`Failed to load projects for use case: ${useCase.name}`);
                    useCasesWithProjects.push({
                        ...useCase,  // ✅ Preserve ALL original properties
                        projects: []  // ✅ Empty projects array on failure
                    });
                }
            } catch (error) {
                console.error(`Error loading projects for use case ${useCase.name}:`, error);
                useCasesWithProjects.push({
                    ...useCase,  // ✅ Preserve ALL original properties
                    projects: []  // ✅ Empty projects array on error
                });
            }
        }
        
        // Cache the grouped data for 30 seconds to prevent duplicate API calls
        this._groupedUseCasesCache = {
            data: useCasesWithProjects,
            timestamp: Date.now()
        };
        
        // Store the enhanced use cases with projects
        this.useCases = useCasesWithProjects;
        
        // Also store the original use cases separately for reference
        this._originalUseCases = this.useCases.filter(uc => !uc.projects);
        
        console.log('✅ Data Manager: Updated useCases with projects:', this.useCases.map(uc => ({
            use_case_id: uc.use_case_id,
            name: uc.name,
            projectCount: uc.projects ? uc.projects.length : 0
        })));
        
        // Debug: Log the actual structure of each use case
        console.log('🔍 Detailed use case structure:', this.useCases.map(uc => ({
            use_case_id: uc.use_case_id,
            name: uc.name,
            hasProjectsProperty: 'projects' in uc,
            projectsType: typeof uc.projects,
            projectsLength: Array.isArray(uc.projects) ? uc.projects.length : 'not array',
            projectsKeys: uc.projects ? Object.keys(uc.projects) : 'no projects'
        })));
        
        return this.useCases;
    }

    // Render projects in the UI (legacy method - now handled by showProjectsForUseCase)
    renderProjects() {
        const container = $('#projectsContainer');
        if (!container.length) {
            console.warn('Projects container not found');
            return;
        }
        
        if (this.projects.length === 0) {
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No projects found</h5>
                    <p class="text-muted">Create your first project to get started</p>
                    <button class="btn btn-primary" onclick="showCreateProjectModal()">
                        <i class="fas fa-plus me-2"></i>Create Project
                    </button>
                </div>
            `);
            return;
        }
        
        // Render projects by category
        let html = '';
        Object.keys(this.categories).forEach(category => {
            html += this.renderProjectCategory(category, this.categories[category]);
        });
        
        container.html(html);
    }

    // Render a project category
    renderProjectCategory(category, projects) {
        const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
        const categoryIcon = this.getCategoryIcon(category);
        
        let html = `
            <div class="category-section mb-4">
                <h5 class="category-title">
                    <i class="${categoryIcon} me-2"></i>${categoryName}
                    <span class="badge bg-primary ms-2">${projects.length}</span>
                </h5>
                <div class="row">
        `;
        
        projects.forEach(project => {
            html += this.renderProjectCard(project);
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }

    // Render a single project card
    renderProjectCard(project) {
        console.log(`🔍 renderProjectCard: Project ${project.name}:`, project);
        console.log(`🔍 renderProjectCard: file_count = ${project.file_count}, type = ${typeof project.file_count}`);
        
        const fileCount = project.file_count || 0;
        const status = project.status || 'active';
        const statusColor = this.getStatusColor(status);
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card project-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${project.name}</h6>
                            <span class="badge bg-${statusColor}">${status}</span>
                        </div>
                        <p class="card-text text-muted small">${project.description || 'No description'}</p>
                        <div class="project-stats">
                            <small class="text-muted">
                                <i class="fas fa-file me-1"></i>${fileCount} files
                            </small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex gap-1 justify-content-center">
                            <button class="btn btn-xs btn-outline-primary btn-view-project" data-project-id="${project.project_id}" title="View Project Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-xs btn-outline-success btn-upload-project" data-project-id="${project.project_id}" title="Upload Files">
                                <i class="fas fa-upload"></i>
                            </button>
                            <button class="btn btn-xs btn-outline-danger btn-delete-project" data-project-id="${project.project_id}" title="Delete Project">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Show use cases in the UI
    async showUseCases() {
        const container = $('#useCasesContainer');
        const projectsSection = $('#projectsSection');
        
        if (!container.length) {
            console.warn('Use cases container not found');
            return;
        }
        
        // Hide projects section, show use cases
        projectsSection.hide();
        container.show(); // Make sure use cases container is visible
        
        // Show loading state
        container.html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="text-muted">Loading Use Cases...</h5>
                <p class="text-muted">Please wait while we load the use cases</p>
            </div>
        `);
        
        try {
            // Group projects by use case (now async)
            const useCasesWithProjects = await this.groupProjectsByUseCase();
            
            if (useCasesWithProjects.length === 0) {
                container.html(`
                    <div class="text-center py-5">
                        <i class="fas fa-sitemap fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">No use cases found</h5>
                        <p class="text-muted">Create your first use case to get started</p>
                    </div>
                `);
                return;
            }
            
            // Render use cases
            let html = '<div class="row">';
            useCasesWithProjects.forEach(useCase => {
                html += this.renderUseCaseCard(useCase);
            });
            html += '</div>';
            
            container.html(html);
        } catch (error) {
            console.error('Error loading use cases:', error);
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h5 class="text-danger">Error Loading Use Cases</h5>
                    <p class="text-muted">Please refresh the page to try again</p>
                </div>
            `);
        }
    }

    // Simple method to show use cases without reloading data
    showUseCasesSimple() {
        const container = $('#useCasesContainer');
        const projectsSection = $('#projectsSection');
        
        if (!container.length) {
            console.warn('Use cases container not found');
            return;
        }
        
        // Reset flag to indicate user is viewing use cases
        this.isViewingProjects = false;
        
        // Hide projects section, show use cases
        projectsSection.hide();
        container.show();
        
        // Render use cases from existing data
        if (!this.useCases || this.useCases.length === 0) {
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-sitemap fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No use cases found</h5>
                    <p class="text-muted">Create your first use case to get started</p>
                </div>
            `);
            return;
        }
        
        // Render use cases
        let html = '<div class="row">';
        this.useCases.forEach(useCase => {
            html += this.renderUseCaseCard(useCase);
        });
        html += '</div>';
        
        container.html(html);
    }

    // Render a single use case card
    renderUseCaseCard(useCase) {
        console.log(`🔍 renderUseCaseCard called for: ${useCase.name}`, {
            id: useCase.id,
            hasProjects: !!useCase.projects,
            projectCount: useCase.projects ? useCase.projects.length : 0,
            projects: useCase.projects
        });
        
        const projectCount = useCase.projects ? useCase.projects.length : 0;
        const categoryIcon = this.getCategoryIcon(useCase.category || 'general');
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card use-case-card h-100" data-use-case-id="${useCase.use_case_id}" style="cursor: pointer;">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">
                                <i class="${categoryIcon} me-2"></i>${useCase.name}
                            </h6>
                            <span class="badge bg-primary">${projectCount} projects</span>
                        </div>
                        <p class="card-text text-muted small">${useCase.description || 'No description'}</p>
                    </div>
                    <div class="card-footer bg-transparent">
                        <button class="btn btn-sm btn-outline-primary w-100" onclick="window.dataManager.selectUseCase('${useCase.use_case_id}')">
                            <i class="fas fa-eye me-1"></i>View Projects
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // Handle use case selection
    selectUseCase(useCaseId) {
        console.log(`🔍 selectUseCase called with ID: ${useCaseId}`);
        console.log(`🔍 Current useCases array:`, this.useCases.map(uc => ({
            use_case_id: uc.use_case_id,
            name: uc.name,
            hasProjects: !!uc.projects,
            projectCount: uc.projects ? uc.projects.length : 0
        })));
        
        const useCase = this.useCases.find(uc => uc.use_case_id === useCaseId);
        if (!useCase) {
            console.error('❌ Use case not found:', useCaseId);
            console.error('❌ Available use case IDs:', this.useCases.map(uc => uc.use_case_id));
            return;
        }
        
        console.log(`✅ Found use case: ${useCase.name} with ${useCase.projects ? useCase.projects.length : 0} projects`);
        this.selectedUseCase = useCase;
        this.showProjectsForUseCase(useCase);
    }

    // Show projects for a specific use case
    showProjectsForUseCase(useCase) {
        const projectsSection = $('#projectsSection');
        const useCasesContainer = $('#useCasesContainer');
        const selectedUseCaseName = $('#selectedUseCaseName');
        const projectsContainer = $('#projectsContainer');
        
        // Set flag to indicate user is viewing projects
        this.isViewingProjects = true;
        
        // Update UI
        selectedUseCaseName.text(useCase.name);
        useCasesContainer.hide();
        projectsSection.show();
        
        console.log(`🔍 showProjectsForUseCase: Use case ${useCase.name} has ${useCase.projects ? useCase.projects.length : 0} projects`);
        console.log(`🔍 Full useCase object:`, useCase);
        console.log(`🔍 useCase.projects property:`, useCase.projects);
        console.log(`🔍 useCase.projects type:`, typeof useCase.projects);
        console.log(`🔍 useCase.projects is array:`, Array.isArray(useCase.projects));
        
        if (useCase.projects) {
            useCase.projects.forEach(project => {
                console.log(`🔍 Project ${project.name}: file_count = ${project.file_count}`);
            });
        } else {
            console.log(`❌ No projects property found on use case:`, useCase);
        }
        
        // Render projects
        if (!useCase.projects || useCase.projects.length === 0) {
            projectsContainer.html(`
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No projects found</h5>
                    <p class="text-muted">This use case has no projects yet</p>
                    <button class="btn btn-primary" onclick="showCreateProjectModal()">
                        <i class="fas fa-plus me-2"></i>Create Project
                    </button>
                </div>
            `);
            return;
        }
        
        // Render projects directly (no category grouping needed for use case view)
        let html = '<div class="row">';
        useCase.projects.forEach(project => {
            html += this.renderProjectCard(project);
        });
        html += '</div>';
        
        projectsContainer.html(html);
    }

    // Get category icon
    getCategoryIcon(category) {
        const icons = {
            'thermal': 'fas fa-fire',
            'structural': 'fas fa-cube',
            'fluid': 'fas fa-water',
            'multi_physics': 'fas fa-atom',
            'industrial': 'fas fa-industry',
            'applications': 'fas fa-cogs',
            'physics': 'fas fa-atom',
            'general': 'fas fa-chart-line'
        };
        return icons[category] || 'fas fa-folder';
    }

    // Get status color
    getStatusColor(status) {
        const colors = {
            'active': 'active',
            'inactive': 'inactive',
            'error': 'error',
            'processing': 'processing'
        };
        return colors[status] || 'inactive';
    }

    // Update project selects
    updateProjectSelects() {
        const selects = ['#uploadProjectSelect', '#urlProjectSelect', '#etlProjectSelect'];
        
        selects.forEach(selectId => {
            const select = $(selectId);
            if (select.length) {
                select.empty();
                select.append('<option value="">Select a project...</option>');
                
                this.projects.forEach(project => {
                    select.append(`<option value="${project.project_id}">${project.name}</option>`);
                });
            }
        });
    }

    // View project details
    viewProject(projectId) {
        console.log(`🔍 Viewing project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Show project details modal or navigate to project details page
        this.showProjectDetails(project);
    }

    // Upload to project
    uploadToProject(projectId) {
        console.log(`📤 Uploading to project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Navigate to file upload section with pre-selected project
        this.navigateToUploadWithProject(project);
    }

    // Delete project
    async deleteProject(projectId) {
        console.log(`🗑️ Deleting project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Show confirmation dialog
        const confirmed = await this.showDeleteConfirmation(project);
        if (!confirmed) {
            return;
        }
        
        // Delete the project
        await this.performProjectDeletion(project);
    }

    // Find project by ID across all use cases
    findProjectById(projectId) {
        console.log(`🔍 findProjectById: Looking for project ID: ${projectId}`);
        console.log(`🔍 findProjectById: Available use cases:`, this.useCases.map(uc => ({
            name: uc.name,
            projectCount: uc.projects ? uc.projects.length : 0,
            projectIds: uc.projects ? uc.projects.map(p => p.project_id) : [],
            sampleProject: uc.projects && uc.projects[0] ? Object.keys(uc.projects[0]) : []
        })));
        
        for (const useCase of this.useCases) {
            if (useCase.projects) {
                const project = useCase.projects.find(p => p.project_id === projectId);
                if (project) {
                    console.log(`✅ findProjectById: Found project ${project.name} in use case ${useCase.name}`);
                    return { ...project, useCase: useCase };
                }
            }
        }
        
        console.log(`❌ findProjectById: Project ${projectId} not found in any use case`);
        return null;
    }

    // Show project details
    async showProjectDetails(project) {
        console.log(`🔍 showProjectDetails: Loading details for project ${project.name}`);
        
        // Show loading state first
        const modalHtml = `
            <div class="modal fade" id="projectDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-folder me-2"></i>${project.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center py-4">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2">Loading project details...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        $('#projectDetailsModal').remove();
        
        // Add modal to body and show it
        $('body').append(modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('projectDetailsModal'));
        modal.show();
        
        try {
            // Fetch detailed project information including files
            console.log(`🔍 Fetching project details for project ID: ${project.project_id}`);
            const response = await fetch(`/api/aasx-etl/projects/${project.project_id}`, {
                headers: this.getAuthHeaders()
            });
            console.log(`🔍 Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch project details: ${response.status}`);
            }
            
            const projectDetails = await response.json();
            console.log(`🔍 Project details loaded:`, projectDetails);
            console.log(`🔍 Project details type:`, typeof projectDetails);
            console.log(`🔍 Project details keys:`, Object.keys(projectDetails));
            
            // Update modal with detailed information
            this.updateProjectDetailsModal(projectDetails);
            
        } catch (error) {
            console.error('❌ Error loading project details:', error);
            this.updateProjectDetailsModal(project, error.message);
        }
    }
    
    // Update project details modal with comprehensive information
    updateProjectDetailsModal(projectDetails, errorMessage = null) {
        console.log(`🔍 updateProjectDetailsModal called with:`, { projectDetails, errorMessage });
        console.log(`🔍 projectDetails type:`, typeof projectDetails);
        console.log(`🔍 projectDetails value:`, projectDetails);
        
        const modalBody = $('#projectDetailsModal .modal-body');
        
        if (errorMessage) {
            console.log(`🔍 Showing error message: ${errorMessage}`);
            modalBody.html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading project details: ${errorMessage}
                </div>
            `);
            return;
        }
        
        if (!projectDetails) {
            console.error(`❌ projectDetails is undefined or null`);
            modalBody.html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error: Project details not available
                </div>
            `);
            return;
        }
        
        const files = projectDetails.files || [];
        const useCase = projectDetails.use_case;
        
        const modalContent = `
            <div class="aasx-project-details">
                <!-- Project Header -->
                <div class="aasx-project-header mb-4">
                    <div class="aasx-project-title-section">
                        <h4 class="aasx-project-title">
                            <i class="fas fa-project-diagram me-2"></i>
                            ${projectDetails.name}
                        </h4>
                        <div class="aasx-project-status">
                            <span class="aasx-status-badge aasx-status-${this.getStatusColor(projectDetails.status || 'active')}">
                                <i class="fas fa-circle me-1"></i>
                                ${projectDetails.status || 'active'}
                            </span>
                        </div>
                    </div>
                    <p class="aasx-project-description">${projectDetails.description || 'No description available'}</p>
                </div>

                <!-- Project Stats Cards -->
                <div class="row g-3 mb-4">
                    <div class="col-md-3">
                        <div class="aasx-stat-card">
                            <div class="aasx-stat-icon">
                                <i class="fas fa-folder"></i>
                            </div>
                            <div class="aasx-stat-content">
                                <div class="aasx-stat-number">${files.length}</div>
                                <div class="aasx-stat-label">Files</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="aasx-stat-card">
                            <div class="aasx-stat-icon">
                                <i class="fas fa-calendar"></i>
                            </div>
                            <div class="aasx-stat-content">
                                <div class="aasx-stat-number">${new Date(projectDetails.created_at).toLocaleDateString()}</div>
                                <div class="aasx-stat-label">Created</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="aasx-stat-card">
                            <div class="aasx-stat-icon">
                                <i class="fas fa-clock"></i>
                            </div>
                            <div class="aasx-stat-content">
                                <div class="aasx-stat-number">${new Date(projectDetails.updated_at).toLocaleDateString()}</div>
                                <div class="aasx-stat-label">Last Updated</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="aasx-stat-card">
                            <div class="aasx-stat-icon">
                                <i class="fas fa-fingerprint"></i>
                            </div>
                            <div class="aasx-stat-content">
                                <div class="aasx-stat-number">${projectDetails.project_id.substring(0, 8)}...</div>
                                <div class="aasx-stat-label">Project ID</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Project Information Grid -->
                <div class="row g-4 mb-4">
                    <!-- Use Case & Tags -->
                    <div class="col-lg-6">
                        <div class="aasx-info-card">
                            <div class="aasx-info-card-header">
                                <h6><i class="fas fa-sitemap me-2"></i>Use Case</h6>
                            </div>
                            <div class="aasx-info-card-body">
                                <div class="aasx-use-case-info">
                                    <span class="aasx-use-case-name">${projectDetails.use_case_name || 'Unknown'}</span>
                                    ${projectDetails.use_case_description ? `<small class="text-muted d-block mt-1">${projectDetails.use_case_description}</small>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tags -->
                    <div class="col-lg-6">
                        <div class="aasx-info-card">
                            <div class="aasx-info-card-header">
                                <h6><i class="fas fa-tags me-2"></i>Tags</h6>
                            </div>
                            <div class="aasx-info-card-body">
                                ${this.renderTags(projectDetails.tags)}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Metadata -->
                ${projectDetails.metadata && Object.keys(projectDetails.metadata).length > 0 ? `
                <div class="aasx-info-card mb-4">
                    <div class="aasx-info-card-header">
                        <h6><i class="fas fa-info-circle me-2"></i>Metadata</h6>
                    </div>
                    <div class="aasx-info-card-body">
                        ${this.renderMetadata(projectDetails.metadata)}
                    </div>
                </div>
                ` : ''}

                <!-- Files Section -->
                <div class="aasx-files-section">
                    <div class="aasx-section-header">
                        <h6><i class="fas fa-file-alt me-2"></i>Files in Project</h6>
                        <span class="aasx-file-count">${files.length} file${files.length !== 1 ? 's' : ''}</span>
                    </div>
                    ${this.renderProjectFiles(files, projectDetails)}
                </div>
            </div>
        `;
        
        modalBody.html(modalContent);
         
        // Add modal footer
        const modalFooter = `
            <div class="modal-footer">
                    <button type="button" class="btn btn-outline-danger" onclick="dataManager.deleteProject('${projectDetails.project_id}')">
                    <i class="fas fa-trash me-1"></i>Delete Project
                </button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" onclick="dataManager.uploadToProject('${projectDetails.project_id}')">
                    <i class="fas fa-upload me-1"></i>Upload Files
                </button>
            </div>
        `;
        
        modalBody.after(modalFooter);
    }
    
    // Render project files with detailed information
    renderProjectFiles(files, projectDetails) {
        if (!files || files.length === 0) {
            return `
                <div class="aasx-empty-state">
                    <div class="aasx-empty-state-icon">
                        <i class="fas fa-file-upload"></i>
                    </div>
                    <h6>No Files Uploaded</h6>
                    <p class="text-muted">This project doesn't have any files yet. Upload your first AASX file to get started.</p>
                    <button class="btn btn-primary btn-sm" onclick="dataManager.uploadToProject('${projectDetails.project_id}')">
                        <i class="fas fa-upload me-1"></i>Upload Files
                    </button>
                </div>
            `;
        }
        
        let filesHtml = `
            <div class="aasx-files-table-container">
                <div class="table-responsive">
                    <table class="table aasx-files-table">
                        <thead>
                            <tr>
                                <th class="aasx-table-header">
                                    <i class="fas fa-file me-1"></i>File Name
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-tasks me-1"></i>Job Type
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-info-circle me-1"></i>Status
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-network-wired me-1"></i>Federated Learning
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-weight-hanging me-1"></i>Size
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-calendar me-1"></i>Upload Date
                                </th>
                                <th class="aasx-table-header">
                                    <i class="fas fa-cogs me-1"></i>Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        files.forEach(file => {
            const statusColor = this.getFileStatusColor(file.status);
            const federatedColor = this.getFederatedLearningColor(file.federated_learning);
            const fileSize = this.formatFileSize(file.size || 0);
            const uploadDate = new Date(file.upload_date || file.created_at).toLocaleDateString();
            
            filesHtml += `
                <tr class="aasx-file-row">
                    <td class="aasx-file-name">
                        <div class="aasx-file-info">
                            <div class="aasx-file-icon">
                                <i class="fas fa-file-code"></i>
                            </div>
                            <div class="aasx-file-details">
                                <div class="aasx-file-title">${file.filename}</div>
                                ${file.description ? `<small class="aasx-file-description">${file.description}</small>` : ''}
                            </div>
                        </div>
                    </td>
                    <td class="aasx-file-job-type">
                        <span class="aasx-job-type-badge aasx-job-type-${file.job_type || 'unknown'}">
                            <i class="fas fa-${file.job_type === 'extraction' ? 'arrow-right' : file.job_type === 'generation' ? 'arrow-left' : 'question'} me-1"></i>
                            ${file.job_type || 'unknown'}
                        </span>
                    </td>
                    <td class="aasx-file-status">
                        <span class="aasx-status-badge aasx-status-${statusColor}">
                            <i class="fas fa-circle me-1"></i>
                            ${file.status || 'unknown'}
                        </span>
                    </td>
                    <td class="aasx-file-federated">
                        <span class="aasx-status-badge aasx-status-${federatedColor}">
                            <i class="fas fa-${file.federated_learning === 'allowed' ? 'check' : 'times'} me-1"></i>
                            ${file.federated_learning || 'not_allowed'}
                        </span>
                    </td>
                    <td class="aasx-file-size">
                        <span class="aasx-size-badge">${fileSize}</span>
                    </td>
                    <td class="aasx-file-date">
                        <span class="aasx-date-badge">${uploadDate}</span>
                    </td>
                    <td class="aasx-file-actions">
                        <div class="aasx-action-buttons">
                            ${file.job_type === 'extraction' ? `
                                <button class="aasx-action-btn aasx-action-view" title="View AASX File in Blazor" onclick="dataManager.viewFileInBlazor('${file.file_id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                            ` : `
                                <button class="aasx-action-btn aasx-action-view aasx-action-disabled" title="ZIP files cannot be viewed in Blazor" disabled>
                                    <i class="fas fa-eye-slash"></i>
                                </button>
                            `}
                            <button class="aasx-action-btn aasx-action-edit" title="Edit File" onclick="dataManager.editFile('${file.file_id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="aasx-action-btn aasx-action-delete" title="Delete File" onclick="dataManager.deleteFile('${file.file_id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        filesHtml += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        return filesHtml;
    }
    
    // Get color for file status
    getFileStatusColor(status) {
        const colors = {
            'not_processed': 'warning',
            'processing': 'info',
            'processed': 'success',
            'failed': 'danger',
            'error': 'danger'
        };
        return colors[status] || 'secondary';
    }
    
    // Get color for federated learning status
    getFederatedLearningColor(federatedLearning) {
        const colors = {
            'allowed': 'success',
            'not_allowed': 'danger',
            'conditional': 'warning'
        };
        return colors[federatedLearning] || 'secondary';
    }
    
    // Format file size
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Render metadata
    renderMetadata(metadata) {
        if (!metadata) {
            return '<p class="text-muted small">No metadata available</p>';
        }
        
        try {
            const metadataObj = typeof metadata === 'string' ? JSON.parse(metadata) : metadata;
            let html = '<div class="small">';
            Object.entries(metadataObj).forEach(([key, value]) => {
                html += `<div><strong>${key}:</strong> ${value}</div>`;
            });
            html += '</div>';
            return html;
        } catch (e) {
            return '<p class="text-muted small">Invalid metadata format</p>';
        }
        }
    
    // View file details
    viewFileDetails(fileId) {
        console.log(`🔍 Viewing file details for file ID: ${fileId}`);
        // TODO: Implement file details view
        showInfo('File details view will be implemented soon');
    }
    
    // View file in Blazor viewer
    async viewFileInBlazor(fileId) {
        try {
            console.log(`🔍 Opening AASX file in Blazor viewer: ${fileId}`);
            
            // Validate file_id
            if (!fileId) {
                showError('Invalid file ID');
                return;
            }
            
            // ✅ ENHANCED BLAZOR URL: Pass file_id directly - Blazor will resolve the correct path via API
            // The backend API now includes job_type in the logical_path for proper file location
            const blazorUrl = `http://localhost:5001/?file=${fileId}`;
            
            console.log(`🌐 Opening Blazor URL: ${blazorUrl}`);
            
            // Open in new tab
            window.open(blazorUrl, '_blank');
            
            showSuccess('Opening file in Blazor viewer...');
            
        } catch (error) {
            console.error('Error opening Blazor viewer:', error);
            showError('Failed to open file viewer');
        }
    }
    
    // Delete file
    async deleteFile(fileId) {
        console.log(`🗑️ Deleting file with ID: ${fileId}`);
        if (confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
            try {
                const response = await fetch(`/api/aasx-etl/files/${fileId}`, {
                    method: 'DELETE',
                    headers: this.getAuthHeaders()
                });
                
                if (response.ok) {
                    showSuccess('File deleted successfully');
                    // Refresh the current view
                    await this.refreshCurrentView();
                } else {
                    showError('Failed to delete file');
                }
            } catch (error) {
                console.error('Error deleting file:', error);
                showError('Error deleting file');
            }
        }
    }
    
    // Navigate to upload section with pre-selected project
    navigateToUploadWithProject(project) {
        // Scroll to file upload section - look for the Bidirectional File Hub section
        const uploadSection = $('.aasx-section-title:contains("Bidirectional File Hub")').closest('.aasx-file-upload-section');
        if (uploadSection.length) {
            $('html, body').animate({
                scrollTop: uploadSection.offset().top - 100
            }, 500);
            
            // Pre-select the use case and project in upload dropdowns
            setTimeout(() => {
                this.preSelectUploadOptions(project);
            }, 600);
        } else {
            showError('File upload section not found. Please make sure you are on the File Upload tab.');
        }
    }

    // Pre-select upload options
    preSelectUploadOptions(project) {
        // Find the use case ID for this project
        const useCaseId = project.useCase ? project.useCase.use_case_id : null;
        
        if (useCaseId) {
            // Select use case in upload dropdowns
            $('.use-case-select').val(useCaseId).trigger('change');
            
            // Wait for projects to load, then select the project
            setTimeout(() => {
                $('.project-select').val(project.project_id).trigger('change');
            }, 1000);
            
            showSuccess(`Ready to upload files to "${project.name}"`);
        }
    }

    // Show delete confirmation dialog
    showDeleteConfirmation(project) {
        return new Promise((resolve) => {
            const modalHtml = `
                <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-exclamation-triangle me-2"></i>Delete Project
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="text-center mb-3">
                                    <i class="fas fa-trash fa-3x text-danger mb-3"></i>
                                    <h5>Are you sure you want to delete this project?</h5>
                                </div>
                                <div class="alert alert-warning">
                                    <strong>Project:</strong> ${project.name}<br>
                                    <strong>Use Case:</strong> ${project.useCase ? project.useCase.name : 'Unknown'}<br>
                                    <strong>Files:</strong> ${project.file_count || 0} files
                                </div>
                                <div class="alert alert-danger">
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    <strong>Warning:</strong> This action cannot be undone. All project files and data will be permanently deleted.
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                                    <i class="fas fa-trash me-1"></i>Delete Project
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            $('#deleteConfirmationModal').remove();
            
            // Add modal to body
            $('body').append(modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
            
            // Handle confirmation
            $('#confirmDeleteBtn').on('click', () => {
                modal.hide();
                resolve(true);
            });
            
            // Handle cancellation
            $('#deleteConfirmationModal').on('hidden.bs.modal', () => {
                resolve(false);
            });
            
            modal.show();
        });
    }

    // Perform project deletion
    async performProjectDeletion(project) {
        try {
            // Show loading state
            showWarning('Deleting project...');
            
            // Call API to delete project
            const response = await fetch(`/api/aasx-etl/projects/${project.project_id}`, {
                method: 'DELETE',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                showSuccess(`Project "${project.name}" deleted successfully`);
                
                // Remove project from local data
                this.removeProjectFromData(project.project_id);
                
                // Refresh the current view
                await this.refreshCurrentView();
                
            } else {
                const errorData = await response.json();
                showError(`Failed to delete project: ${errorData.detail || 'Unknown error'}`);
            }
            
        } catch (error) {
            console.error('Error deleting project:', error);
            showError('Failed to delete project. Please try again.');
        }
    }

    // Remove project from local data
    removeProjectFromData(projectId) {
        for (const useCase of this.useCases) {
            if (useCase.projects) {
                const projectIndex = useCase.projects.findIndex(p => p.project_id === projectId);
                if (projectIndex !== -1) {
                    useCase.projects.splice(projectIndex, 1);
                    break;
                }
            }
        }
    }

    // Refresh current view
    async refreshCurrentView() {
        // If we're viewing a specific use case, refresh that view
        if (this.selectedUseCase) {
            this.showProjectsForUseCase(this.selectedUseCase);
        } else {
            // If we're viewing all use cases, refresh that view
            await this.showUseCases();
        }
    }

    // Render tags
    renderTags(tags) {
        if (!tags) return '<span class="text-muted">No tags</span>';
        
        try {
            const tagArray = typeof tags === 'string' ? JSON.parse(tags) : tags;
            return tagArray.map(tag => 
                `<span class="badge bg-light text-dark me-1">${tag}</span>`
            ).join('');
        } catch (e) {
            return '<span class="text-muted">Invalid tags</span>';
        }
    }

    showDatabaseError(message) {
        showError(message);
        console.error('Database Error:', message);
    }
}

// Export the class
export default DataManager;