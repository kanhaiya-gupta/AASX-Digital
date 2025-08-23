/**
 * Dropdown Manager for AASX Module
 * Manages dropdown functionality across the AASX module
 */

import { showError } from '/static/js/shared/alerts.js';

export class DropdownManager {
    constructor() {
        this.useCases = [];
        this.projects = [];
        this.files = [];
        this.currentUseCaseId = null;
        this.currentProjectId = null;
        this.isInitialized = false;
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
    }

    async init() {
        if (this.isInitialized) {
            console.log('⚠️ Dropdown Manager already initialized, skipping...');
            return;
        }
        
        console.log('🔄 Dropdown Manager initializing...');
        
        // Wait for auth manager to be ready first
        await this.waitForAuthManager();
        
        console.log('📋 Dropdown Manager: Loading use cases...');
        await this.loadUseCases();
        
        console.log('🔧 Dropdown Manager: Setting up event listeners...');
        this.setupEventListeners();
        
        this.isInitialized = true;
        console.log('✅ Dropdown Manager initialized');
        console.log('📊 Dropdown Manager: Final initialization status:', {
            isInitialized: this.isInitialized,
            useCasesCount: this.useCases ? this.useCases.length : 'undefined',
            isReady: this.isReady()
        });
    }





    /**
     * Wait for global auth manager to be ready
     */
    async waitForAuthManager() {
        console.log('🔐 Dropdown Manager: Waiting for global auth manager...');
        
        // Wait for global auth manager to be ready
        while (!window.authManager) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Dropdown Manager: Global auth manager ready');
        
        // Initial auth state setup
        this.updateAuthState();
        
        // Listen for auth changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Dropdown Manager: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        // 🚫 CRITICAL FIX: Remove duplicate loginSuccess listener - PostLoginOrchestrator handles this
        // window.addEventListener('loginSuccess', async () => {
        //     console.log('🔐 Dropdown Manager: Login success detected');
        //     this.updateAuthState();
        //     
        //     // 🚀 WORLD-CLASS: Immediately refresh user data after login
        //     console.log('🔄 Dropdown Manager: Refreshing user data after login...');
        //     try {
        //             await this.loadUseCases();
        //             console.log('✅ Dropdown Manager: User data refreshed successfully after login');
        //         } catch (error) {
        //             console.error('❌ Dropdown Manager: Failed to refresh user data after login:', error);
        //     }
        // });
        
        window.addEventListener('logout', () => {
            console.log('🔐 Dropdown Manager: Logout detected');
            this.updateAuthState();
        });
    }

    /**
     * Update authentication state from global auth manager
     */
    updateAuthState() {
        if (!window.authManager) return;
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 Dropdown Manager: Auth state update:', sessionInfo);
            
            // Update local state based on global auth manager
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            
        } catch (error) {
            console.warn('⚠️ Dropdown Manager: Error updating auth state:', error);
        }
    }

    /**
     * Get current authentication state from global auth manager
     */
    getCurrentAuthState() {
        // Try multiple ways to get the auth state
        if (window.authSystemManager && window.authSystemManager.authManager) {
            const state = window.authSystemManager.authManager.getCurrentState();
            console.log('🔐 Dropdown Manager: Got auth state from authSystemManager:', state);
            return state;
        }
        
        // Fallback: check if we have a stored token
        const token = this.getStoredToken();
        if (token) {
            console.log('🔐 Dropdown Manager: Using fallback auth state (token exists)');
            return { isAuthenticated: true, user: { username: 'authenticated_user' } };
        }
        
        console.log('🔐 Dropdown Manager: No auth state available, defaulting to unauthenticated');
        return { isAuthenticated: false, user: null };
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Get current auth state and token
        const currentAuthState = this.getCurrentAuthState();
        const token = this.getStoredToken();
        
        if (token) {
            console.log(`🔐 Dropdown Manager: Auth token available - making authenticated request (User: ${currentAuthState.user?.username || 'Unknown'})`);
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.log(`🔐 Dropdown Manager: No auth token available - making unauthenticated request (Auth: ${currentAuthState.isAuthenticated ? 'Yes' : 'No'})`);
        }
        
        return headers;
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

    setupEventListeners() {
        // Use case selection handlers
        $('.use-case-select').on('change', (e) => {
            const useCaseId = $(e.target).val();
            this.onUseCaseChange(useCaseId, $(e.target).closest('.dropdown-section'));
        });

        // Project selection handlers
        $('.project-select').on('change', (e) => {
            const projectId = $(e.target).val();
            this.onProjectChange(projectId, $(e.target).closest('.dropdown-section'));
        });
    }

    async loadUseCases() {
        try {
            // Get current auth state from global auth manager
            const currentAuthState = this.getCurrentAuthState();
            console.log(`🔐 Dropdown Manager: Loading use cases with auth: ${currentAuthState.isAuthenticated ? 'Yes' : 'No'}`);
            
            const response = await fetch('/api/aasx-etl/use-cases', {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                this.useCases = await response.json();
                console.log(`📋 Loaded ${this.useCases.length} use cases`);
                
                // Don't auto-populate here - let components request it when ready
                // this.populateUseCaseDropdowns();
            } else {
                console.error('❌ Failed to load use cases:', response.status, response.statusText);
                this.useCases = []; // Ensure it's always an array
            }
        } catch (error) {
            console.error('❌ Error loading use cases:', error);
            this.useCases = []; // Ensure it's always an array
        }
        
        // Log final state
        console.log(`📊 Dropdown Manager: Final use cases state:`, {
            useCases: this.useCases,
            length: this.useCases ? this.useCases.length : 'undefined',
            isReady: this.isReady()
        });
    }

    async loadProjectsForUseCase(useCaseId) {
        try {
            console.log(`🔍 Dropdown Manager: Loading projects for use case ${useCaseId}`);
            // Get current auth state from global auth manager
            const currentAuthState = this.getCurrentAuthState();
            console.log(`🔐 Dropdown Manager: Auth state: ${currentAuthState.isAuthenticated ? 'Authenticated' : 'Demo mode'}`);
            
            const response = await fetch(`/api/aasx-etl/use-cases/${useCaseId}/projects`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                this.projects = await response.json();
                console.log(`📁 Dropdown Manager: Loaded ${this.projects.length} projects for use case ${useCaseId}`);
                console.log(`📋 Dropdown Manager: Project names:`, this.projects.map(p => p.name));
                return this.projects;
            } else {
                console.error('Failed to load projects for use case');
                return [];
            }
        } catch (error) {
            console.error('Error loading projects:', error);
            return [];
        }
    }

    async loadFilesForProject(projectId) {
        try {
            const response = await fetch(`/api/aasx-etl/projects/${projectId}/files`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                console.log(`📄 Loaded ${data.files ? data.files.length : 0} files for project ${projectId}`);
                console.log(`📄 Files data structure:`, data);
                
                // Return the files array from the response
                return data.files || [];
            } else {
                console.error('Failed to load files for project');
                return [];
            }
        } catch (error) {
            console.error('Error loading files:', error);
            return [];
        }
    }

    populateUseCaseDropdowns() {
        console.log('🔄 Dropdown Manager: Populating use case dropdowns...');
        console.log(`📋 Dropdown Manager: Available use cases:`, this.useCases);
        
        // Check if jQuery is available
        if (typeof $ === 'undefined') {
            console.warn('⚠️ Dropdown Manager: jQuery not available, using vanilla JS');
            this.populateUseCaseDropdownsVanilla();
            return;
        }
        
        const useCaseSelects = $('.use-case-select');
        console.log(`🔍 Dropdown Manager: Found ${useCaseSelects.length} use case selects with jQuery`);
        
        if (useCaseSelects.length === 0) {
            console.warn('⚠️ Dropdown Manager: No use case selects found with jQuery, trying vanilla JS');
            this.populateUseCaseDropdownsVanilla();
            return;
        }
        
        useCaseSelects.each((index, element) => {
            const $select = $(element);
            console.log(`🔧 Dropdown Manager: Populating jQuery select ${index}:`, element.id || element.className);
            
            $select.empty();
            $select.append('<option value="">Choose a use case...</option>');
            
            this.useCases.forEach(useCase => {
                $select.append(`<option value="${useCase.use_case_id}">${useCase.name}</option>`);
            });
        });
        
        // Also try vanilla JS as fallback
        this.populateUseCaseDropdownsVanilla();
        
        // Also populate ETL Pipeline dropdowns specifically
        this.populateETLPipelineDropdowns();
    }

    populateUseCaseDropdownsVanilla() {
        console.log('🔄 Dropdown Manager: Populating use case dropdowns with vanilla JS...');
        
        const useCaseSelects = document.querySelectorAll('.use-case-select');
        console.log(`🔍 Dropdown Manager: Found ${useCaseSelects.length} use case selects with vanilla JS`);
        
        if (useCaseSelects.length === 0) {
            console.warn('⚠️ Dropdown Manager: No use case selects found with vanilla JS either');
            console.log('🔍 Dropdown Manager: Searching for any select elements with use-case in ID or class...');
            
            // Try to find selects by ID pattern
            const allSelects = document.querySelectorAll('select');
            const useCaseSelectsById = Array.from(allSelects).filter(select => 
                select.id && select.id.toLowerCase().includes('usecase')
            );
            console.log(`🔍 Dropdown Manager: Found ${useCaseSelectsById.length} selects with 'usecase' in ID:`, 
                useCaseSelectsById.map(s => s.id));
            
            if (useCaseSelectsById.length > 0) {
                console.log('🔧 Dropdown Manager: Using selects found by ID pattern');
                useCaseSelectsById.forEach((select, index) => {
                    this.populateSingleUseCaseDropdown(select, index);
                });
                
                // Also populate ETL Pipeline dropdowns specifically
                this.populateETLPipelineDropdowns();
                return;
            }
            
            console.error('❌ Dropdown Manager: No use case selects found by any method');
            return;
        }
        
        useCaseSelects.forEach((select, index) => {
            this.populateSingleUseCaseDropdown(select, index);
        });
        
        // Also populate ETL Pipeline dropdowns specifically
        this.populateETLPipelineDropdowns();
        
        console.log(`✅ Dropdown Manager: Populated ${useCaseSelects.length} use case dropdowns with vanilla JS`);
    }

    populateSingleUseCaseDropdown(select, index) {
        console.log(`🔧 Dropdown Manager: Populating select ${index}:`, select.id || select.className);
        
        // Clear existing options
        select.innerHTML = '<option value="">Choose a use case...</option>';
        
        // Add use cases
        this.useCases.forEach(useCase => {
            const option = document.createElement('option');
            option.value = useCase.use_case_id;
            option.textContent = useCase.name;
            select.appendChild(option);
        });
        
        console.log(`✅ Dropdown Manager: Populated select ${index} with ${this.useCases.length} use cases`);
    }

    async populateProjectDropdown(useCaseId, container) {
        const $projectSelect = container.find('.project-select');
        $projectSelect.empty();
        $projectSelect.append('<option value="">Choose a project...</option>');
        
        if (!useCaseId) {
            $projectSelect.append('<option value="" disabled>Select a use case first to see available projects</option>');
            return;
        }

        const projects = await this.loadProjectsForUseCase(useCaseId);
        console.log(`🔧 Dropdown Manager: Populating dropdown with ${projects.length} projects`);
        projects.forEach(project => {
            $projectSelect.append(`<option value="${project.project_id}">${project.name}</option>`);
        });
        console.log(`✅ Dropdown Manager: Dropdown populated with ${$projectSelect.find('option').length - 1} project options`);
    }

    async populateFileDropdown(projectId, container) {
        const $fileSelect = container.find('.file-select');
        const $fileList = container.find('.file-list');
        
        if (!projectId) {
            $fileList.html('<p class="text-muted">Select a project to view available files for ETL processing</p>');
            return;
        }

        const files = await this.loadFilesForProject(projectId);
        const unprocessedFiles = files.filter(file => file.status !== 'processed');
        
        if (unprocessedFiles.length === 0) {
            $fileList.html('<p class="text-muted">No unprocessed files available for ETL processing</p>');
            return;
        }

        let html = '<div class="file-selection-list">';
        unprocessedFiles.forEach(file => {
            const statusColor = this.getFileStatusColor(file.status);
            const statusText = this.getFileStatusText(file.status);
            
            html += `
                <div class="file-item d-flex align-items-center p-2 border-bottom" data-job-type="${file.job_type || ''}">
                    <div class="form-check me-3">
                        <input class="form-check-input file-checkbox" type="checkbox" 
                               value="${file.file_id}" id="file_${file.file_id}">
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${file.filename}</h6>
                        <small class="text-muted">${file.description || 'No description'}</small>
                        <br>
                        <small class="text-muted">
                            <i class="fas fa-hdd me-1"></i>${this.formatFileSize(file.size || 0)}
                        </small>
                    </div>
                    <span class="badge ${statusColor}">${statusText}</span>
                </div>
            `;
        });
        html += '</div>';
        
        $fileList.html(html);
    }

    async onUseCaseChange(useCaseId, container) {
        this.currentUseCaseId = useCaseId;
        
        // Reset project selection
        const $projectSelect = container.find('.project-select');
        $projectSelect.val('');
        
        // Reset file selection
        const $fileList = container.find('.file-list');
        $fileList.empty();
        
        if (useCaseId) {
            await this.populateProjectDropdown(useCaseId, container);
        } else {
            $projectSelect.empty();
            $projectSelect.append('<option value="">Choose a project...</option>');
            $projectSelect.append('<option value="" disabled>Select a use case first to see available projects</option>');
        }
    }

    async onProjectChange(projectId, container) {
        this.currentProjectId = projectId;
        
        if (projectId) {
            await this.populateFileDropdown(projectId, container);
        } else {
            const $fileList = container.find('.file-list');
            $fileList.html('<p class="text-muted">Select a project to view available files for ETL processing</p>');
        }
    }

    getSelectedFiles(container) {
        const selectedFiles = [];
        container.find('.file-checkbox:checked').each(function() {
            selectedFiles.push($(this).val());
        });
        return selectedFiles;
    }

    getFileStatusColor(status) {
        const colors = {
            'processed': 'bg-success',
            'processing': 'bg-warning',
            'failed': 'bg-danger',
            'not_processed': 'bg-secondary'
        };
        return colors[status] || 'bg-secondary';
    }

    getFileStatusText(status) {
        const texts = {
            'processed': 'Processed',
            'processing': 'Processing',
            'failed': 'Failed',
            'not_processed': 'Pending'
        };
        return texts[status] || 'Unknown';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Public methods for external access
    getCurrentUseCaseId() {
        return this.currentUseCaseId;
    }

    getCurrentProjectId() {
        return this.currentProjectId;
    }

    /**
     * Get all loaded use cases
     * @returns {Array} Array of use cases
     */
    getUseCases() {
        return this.useCases || [];
    }

    /**
     * Check if the dropdown manager has use cases loaded
     * @returns {boolean} True if use cases are loaded, false otherwise
     */
    hasUseCases() {
        return this.useCases && this.useCases.length > 0;
    }

    /**
     * Ensure use cases are loaded, reload if necessary
     */
    async ensureUseCasesLoaded() {
        if (!this.hasUseCases()) {
            console.log('🔄 Dropdown Manager: No use cases loaded, loading now...');
            await this.loadUseCases();
        }
        return this.hasUseCases();
    }

    /**
     * Populate dropdowns for a specific component
     * @param {string} componentId - ID of the component requesting population
     */
    async populateDropdownsForComponent(componentId) {
        console.log(`🔄 Dropdown Manager: Populating dropdowns for component ${componentId}`);
        
        // Ensure use cases are loaded first
        const hasUseCases = await this.ensureUseCasesLoaded();
        if (!hasUseCases) {
            console.warn('⚠️ Dropdown Manager: No use cases available for population');
            return false;
        }
        
        // Populate use case dropdowns
        this.populateUseCaseDropdowns();
        
        // If this is the file-upload component, also populate ETL Pipeline dropdowns
        if (componentId === 'file-upload') {
            this.populateETLPipelineDropdowns();
        }
        
        console.log(`✅ Dropdown Manager: Dropdowns populated for component ${componentId}`);
        return true;
    }

    /**
     * Populate ETL Pipeline dropdowns specifically
     */
    populateETLPipelineDropdowns() {
        console.log('🔄 Dropdown Manager: Populating ETL Pipeline dropdowns...');
        
        // Find ETL Pipeline use case select
        const etlUseCaseSelect = document.getElementById('useCaseSelect');
        if (etlUseCaseSelect) {
            console.log('🔧 Dropdown Manager: Populating ETL use case select');
            
            // Clear existing options
            etlUseCaseSelect.innerHTML = '<option value="">Choose a use case...</option>';
            
            // Add use cases
            this.useCases.forEach(useCase => {
                const option = document.createElement('option');
                option.value = useCase.use_case_id;
                option.textContent = useCase.name;
                etlUseCaseSelect.appendChild(option);
            });
            
            console.log(`✅ Dropdown Manager: Populated ETL use case dropdown with ${this.useCases.length} options`);
        } else {
            console.log('⚠️ Dropdown Manager: ETL use case select not found');
        }
    }

    /**
     * Populate ETL Pipeline dropdowns on demand (for when ETL Pipeline is ready)
     */
    populateETLPipelineDropdownsOnDemand() {
        console.log('🔄 Dropdown Manager: Populating ETL Pipeline dropdowns on demand...');
        
        if (!this.isReady()) {
            console.warn('⚠️ Dropdown Manager: Not ready for ETL Pipeline population');
            return false;
        }
        
        this.populateETLPipelineDropdowns();
        return true;
    }

    /**
     * Refresh ETL Pipeline dropdowns (for refresh button)
     */
    async refreshETLPipelineDropdowns() {
        console.log('🔄 Dropdown Manager: Refreshing ETL Pipeline dropdowns...');
        
        try {
            // Reload use cases
            await this.loadUseCases();
            
            // Populate ETL Pipeline dropdowns
            this.populateETLPipelineDropdowns();
            
            console.log('✅ Dropdown Manager: ETL Pipeline dropdowns refreshed');
            return true;
        } catch (error) {
            console.error('❌ Dropdown Manager: Failed to refresh ETL Pipeline dropdowns:', error);
            return false;
        }
    }

    /**
     * Force refresh and populate all dropdowns
     */
    async refreshAndPopulateAll() {
        console.log('🔄 Dropdown Manager: Refreshing and populating all dropdowns...');
        
        try {
            await this.loadUseCases();
            this.populateUseCaseDropdowns();
            
            // Also populate ETL Pipeline dropdowns specifically
            this.populateETLPipelineDropdowns();
            
            console.log('✅ Dropdown Manager: All dropdowns refreshed and populated');
        } catch (error) {
            console.error('❌ Dropdown Manager: Failed to refresh dropdowns:', error);
        }
    }

    getProjects() {
        return this.projects;
    }

    getFiles() {
        return this.files;
    }

    destroy() {
        // Remove event listeners
        $('.use-case-select').off('change');
        $('.project-select').off('change');
        
        // Clear data
        this.useCases = [];
        this.projects = [];
        this.files = [];
        this.currentUseCaseId = null;
        this.currentProjectId = null;
        this.isInitialized = false;
        
        console.log('🧹 Dropdown Manager destroyed');
    }

    /**
     * Handle use case change and populate project dropdown
     * @param {string} useCaseId - Selected use case ID
     * @param {string} projectSelectId - ID of the project select element to populate
     */
    async handleUseCaseChange(useCaseId, projectSelectId) {
        if (!useCaseId) return;
        
        try {
            console.log(`🔄 Dropdown Manager: Handling use case change to ${useCaseId} for project select ${projectSelectId}`);
            
            // Load projects for the selected use case
            const projects = await this.loadProjectsForUseCase(useCaseId);
            
            // Find the project select element
            const projectSelect = document.getElementById(projectSelectId);
            if (!projectSelect) {
                console.warn(`⚠️ Dropdown Manager: Project select element ${projectSelectId} not found`);
                return;
            }
            
            // Clear existing options
            projectSelect.innerHTML = '<option value="">Choose a project...</option>';
            
            // Add projects
            if (projects && projects.length > 0) {
                projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.project_id;
                    option.textContent = project.name;
                    projectSelect.appendChild(option);
                });
                
                console.log(`✅ Dropdown Manager: Populated project dropdown with ${projects.length} options`);
            } else {
                projectSelect.innerHTML = '<option value="">Choose a project...</option><option value="" disabled>No projects available for this use case</option>';
                console.log('⚠️ Dropdown Manager: No projects available for the selected use case');
            }
        } catch (error) {
            console.error('❌ Dropdown Manager: Failed to handle use case change:', error);
        }
    }

    /**
     * Check if the dropdown manager is ready and accessible
     * @returns {boolean} True if ready, false otherwise
     */
    isReady() {
        // Basic readiness: just check if initialized
        const basicReady = this.isInitialized;
        
        // Full readiness: initialized + has use cases
        const fullReady = this.isInitialized && this.useCases && this.useCases.length > 0;
        
        if (!basicReady) {
            console.log('⚠️ Dropdown Manager: Not even basic ready. Status:', {
                isInitialized: this.isInitialized
            });
            return false;
        }
        
        if (!fullReady) {
            console.log('⚠️ Dropdown Manager: Basic ready but no use cases yet. Status:', {
                isInitialized: this.isInitialized,
                useCases: this.useCases,
                useCasesLength: this.useCases ? this.useCases.length : 'undefined',
                useCasesType: typeof this.useCases
            });
            // Still return true for basic readiness
            return true;
        }
        
        console.log('✅ Dropdown Manager: Fully ready with use cases');
        return true;
    }

    /**
     * Check if the dropdown manager has use cases loaded
     * @returns {boolean} True if use cases are loaded, false otherwise
     */
    hasUseCases() {
        return this.useCases && this.useCases.length > 0;
    }

    /**
     * Ensure use cases are loaded, reload if necessary
     */
    async ensureUseCasesLoaded() {
        if (!this.hasUseCases()) {
            console.log('🔄 Dropdown Manager: No use cases loaded, loading now...');
            await this.loadUseCases();
        }
        return this.hasUseCases();
    }

    /**
     * Get initialization status
     * @returns {Object} Status object with details
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            useCasesCount: this.useCases ? this.useCases.length : 0,
            projectsCount: this.projects ? this.projects.length : 0,
            filesCount: this.files ? this.files.length : 0,
            isAuthenticated: this.isAuthenticated,
            currentUser: this.currentUser
        };
    }

    /**
     * Manually trigger dropdown population (for testing/debugging)
     * @param {string} componentId - ID of the component requesting population
     */
    manualPopulateDropdowns(componentId = 'manual') {
        console.log(`🔧 Dropdown Manager: Manual dropdown population requested by ${componentId}`);
        
        if (!this.isReady()) {
            console.warn('⚠️ Dropdown Manager: Not ready for manual population');
            const status = this.getStatus();
            console.log('📊 Current status:', status);
            return false;
        }
        
        try {
            this.populateUseCaseDropdowns();
            console.log('✅ Dropdown Manager: Manual population completed');
            return true;
        } catch (error) {
            console.error('❌ Dropdown Manager: Manual population failed:', error);
            return false;
        }
    }

    /**
     * Debug: Show all available select elements
     */
    debugShowAllSelects() {
        console.log('🔍 Dropdown Manager: Debug - Searching for all select elements...');
        
        const allSelects = document.querySelectorAll('select');
        console.log(`📋 Found ${allSelects.length} total select elements:`, 
            Array.from(allSelects).map(s => ({
                id: s.id,
                className: s.className,
                name: s.name,
                tagName: s.tagName
            }))
        );
        
        const useCaseSelects = document.querySelectorAll('.use-case-select');
        console.log(`🎯 Found ${useCaseSelects.length} use-case-select elements:`, 
            Array.from(useCaseSelects).map(s => ({
                id: s.id,
                className: s.className,
                name: s.name
            }))
        );
        
        const projectSelects = document.querySelectorAll('.project-select');
        console.log(`🎯 Found ${projectSelects.length} project-select elements:`, 
            Array.from(projectSelects).map(s => ({
                id: s.id,
                className: s.className,
                name: s.name
            }))
        );
    }
}

// Global instance
export const dropdownManager = new DropdownManager(); 