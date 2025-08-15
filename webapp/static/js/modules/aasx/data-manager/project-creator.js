/**
 * Project Creator Module
 * Handles project creation functionality including:
 * - Creating projects in existing use cases
 * - Creating new use cases with projects
 */

class ProjectCreator {
    constructor() {
        this.currentCreationType = null; // 'existing' or 'new'
        this.useCases = [];
        this.isInitialized = false;
        
        // Authentication state (will be updated by global auth manager)
        this.isAuthenticated = false;
        this.currentUser = null;
        
        // Initialize asynchronously
        this.init().catch(error => {
            console.error('❌ Project Creator initialization failed:', error);
        });
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Project Creator initializing...');
        

        
        // Check if modal elements exist
        if ($('#projectCreationModal').length === 0) {
            console.error('❌ Project Creator: Modal not found!');
            return;
        }
        
        if ($('#existingUseCaseOption').length === 0) {
            console.error('❌ Project Creator: Existing use case option not found!');
            return;
        }
        
        if ($('#newUseCaseOption').length === 0) {
            console.error('❌ Project Creator: New use case option not found!');
            return;
        }
        
        console.log('✅ Project Creator: Modal elements found');
        
        this.setupEventListeners();
        this.loadUseCases();
        this.isInitialized = true;
        console.log('✅ Project Creator initialized successfully');
    }





    /**
     * Wait for global auth manager to be ready
     */
    async waitForAuthManager() {
        console.log('🔐 Project Creator: Waiting for global auth manager...');
        
        // Wait for global auth manager to be ready
        while (!window.authManager) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('✅ Project Creator: Global auth manager ready');
        
        // Initial auth state setup
        this.updateAuthState();
        
        // Listen for auth changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Project Creator: Auth state changed, updating...');
            this.updateAuthState();
        });
        
        // 🚫 CRITICAL FIX: Remove duplicate loginSuccess listener - PostLoginOrchestrator handles this
        // window.addEventListener('loginSuccess', async () => {
        //     console.log('🔐 Project Creator: Login success detected');
        //     this.updateAuthState();
        //     
        //     // 🚀 WORLD-CLASS: Immediately refresh user data after login
        //     console.log('🔄 Project Creator: Refreshing user data after login...');
        //     try {
        //             await this.loadUseCase();
        //             console.log('✅ Project Creator: User data refreshed successfully after login');
        //         } catch (error) {
        //             console.error('❌ Project Creator: Failed to refresh user data after login:', error);
        //         }
        // });
        
        window.addEventListener('logout', () => {
            console.log('🔐 Project Creator: Logout detected');
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
            console.log('🔐 Project Creator: Auth state update:', sessionInfo);
            
            // Update local state based on global auth manager
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            
        } catch (error) {
            console.warn('⚠️ Project Creator: Error updating auth state:', error);
        }
    }

    /**
     * Get current authentication state from global auth manager
     */
    getCurrentAuthState() {
        // Try multiple ways to get the auth state
        if (window.authSystemManager && window.authSystemManager.authManager) {
            const state = window.authSystemManager.authManager.getCurrentState();
            console.log('🔐 Project Creator: Got auth state from authSystemManager:', state);
            return state;
        }
        
        // Fallback: check if we have a stored token
        const token = this.getStoredToken();
        if (token) {
            console.log('🔐 Project Creator: Using fallback auth state (token exists)');
            return { isAuthenticated: true, user: { username: 'authenticated_user' } };
        }
        
        console.log('🔐 Project Creator: No auth state available, defaulting to unauthenticated');
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
        
        if (!token) {
            console.log(`🔐 Project Creator: No auth token available - making unauthenticated request (Auth: ${currentAuthState.isAuthenticated ? 'Yes' : 'No'})`);
        } else {
            console.log(`🔐 Project Creator: Auth token available - making authenticated request (User: ${currentAuthState.user?.username || 'Unknown'})`);
            headers['Authorization'] = `Bearer ${token}`;
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
        console.log('🔧 Project Creator: Setting up event listeners...');
        
        // Creation type selection
        $('#existingUseCaseOption').on('click', () => {
            console.log('🖱️ Project Creator: Existing use case option clicked');
            this.selectCreationType('existing');
        });
        $('#newUseCaseOption').on('click', () => {
            console.log('🖱️ Project Creator: New use case option clicked');
            this.selectCreationType('new');
        });

        // Create project button
        $('#createProjectBtn').on('click', () => {
            console.log('🖱️ Project Creator: Create project button clicked');
            this.createProject();
        });

        // Modal events
        $('#projectCreationModal').on('show.bs.modal', () => this.onModalShow());
        $('#projectCreationModal').on('hidden.bs.modal', () => this.onModalHide());

        // Form validation
        this.setupFormValidation();
        
        console.log('✅ Project Creator: Event listeners setup complete');
    }

    setupFormValidation() {
        // Real-time validation for required fields
        $('#projectName, #newProjectName, #newUseCaseName, #newUseCaseDescription, #newUseCaseCategory').on('input', () => {
            this.validateForm();
        });

        $('#existingUseCaseSelect').on('change', () => {
            this.validateForm();
        });
    }

    validateForm() {
        const createBtn = $('#createProjectBtn');
        let isValid = false;

        if (this.currentCreationType === 'existing') {
            const useCaseSelected = $('#existingUseCaseSelect').val() !== '';
            const projectName = $('#projectName').val().trim() !== '';
            isValid = useCaseSelected && projectName;
        } else if (this.currentCreationType === 'new') {
            const useCaseName = $('#newUseCaseName').val().trim() !== '';
            const useCaseDescription = $('#newUseCaseDescription').val().trim() !== '';
            const useCaseCategory = $('#newUseCaseCategory').val() !== '';
            const projectName = $('#newProjectName').val().trim() !== '';
            isValid = useCaseName && useCaseDescription && useCaseCategory && projectName;
        }

        createBtn.prop('disabled', !isValid);
    }

    async loadUseCases() {
        try {
            console.log('📋 Loading use cases for project creation...');
            // Get current auth state from global auth manager
            const currentAuthState = this.getCurrentAuthState();
            console.log(`🔐 Project Creator: Auth state: ${currentAuthState.isAuthenticated ? 'Authenticated' : 'Demo mode'}`);
            
            const response = await fetch('/api/aasx-etl/use-cases', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                this.useCases = await response.json();
                this.populateUseCaseDropdown();
                console.log(`✅ Loaded ${this.useCases.length} use cases`);
            } else {
                console.error('❌ Failed to load use cases:', response.status);
            }
        } catch (error) {
            console.error('❌ Error loading use cases:', error);
        }
    }

    populateUseCaseDropdown() {
        const select = $('#existingUseCaseSelect');
        select.empty();
        select.append('<option value="">Choose a use case...</option>');
        
        this.useCases.forEach(useCase => {
            select.append(`<option value="${useCase.id}">${useCase.name}</option>`);
        });
    }

    selectCreationType(type) {
        console.log('🎯 Project Creator: Selecting creation type:', type);
        this.currentCreationType = type;
        
        // Update UI
        $('.creation-option').removeClass('selected');
        if (type === 'existing') {
            $('#existingUseCaseOption').addClass('selected');
            $('#existingUseCaseForm').show();
            $('#newUseCaseForm').hide();
            console.log('✅ Project Creator: Showing existing use case form');
        } else {
            $('#newUseCaseOption').addClass('selected');
            $('#existingUseCaseForm').hide();
            $('#newUseCaseForm').show();
            console.log('✅ Project Creator: Showing new use case form');
        }
        
        this.validateForm();
    }

    onModalShow() {
        // Reset form when modal opens
        this.resetForm();
        this.currentCreationType = null;
        $('.creation-option').removeClass('selected');
        $('#existingUseCaseForm, #newUseCaseForm').hide();
        $('#createProjectBtn').prop('disabled', true);
    }

    onModalHide() {
        // Clean up when modal closes
        this.resetForm();
    }

    resetForm() {
        // Reset all form fields
        $('#projectCreationModal input, #projectCreationModal textarea, #projectCreationModal select').val('');
        $('#existingUseCaseForm, #newUseCaseForm').hide();
        $('.creation-option').removeClass('selected');
        $('#createProjectBtn').prop('disabled', true);
    }

    async createProject() {
        if (!this.currentCreationType) {
            this.showError('Please select a creation type');
            return;
        }

        try {
            $('#createProjectBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Creating...');

            if (this.currentCreationType === 'existing') {
                await this.createProjectInExistingUseCase();
            } else {
                await this.createNewUseCaseWithProject();
            }

        } catch (error) {
            console.error('❌ Error creating project:', error);
            this.showError('Failed to create project: ' + error.message);
        } finally {
            $('#createProjectBtn').prop('disabled', false).html('<i class="fas fa-plus me-2"></i>Create Project');
        }
    }

    async createProjectInExistingUseCase() {
        const useCaseId = $('#existingUseCaseSelect').val();
        const projectName = $('#projectName').val().trim();
        const projectDescription = $('#projectDescription').val().trim();
        const projectTags = this.parseTags($('#projectTags').val());
        const projectIndustry = $('#projectIndustry').val();
        const projectComplexity = $('#projectComplexity').val();
        const projectDuration = $('#projectDuration').val();
        const projectDataPoints = $('#projectDataPoints').val() ? parseInt($('#projectDataPoints').val()) : null;

        // Validate required fields
        if (!useCaseId || !projectName) {
            throw new Error('Use case and project name are required');
        }

        // Prepare project data
        const projectData = {
            name: projectName,
            description: projectDescription || null,
            tags: projectTags,
            use_case_id: useCaseId,
            metadata: {
                industry: projectIndustry || null,
                complexity: projectComplexity || null,
                expected_duration: projectDuration || null,
                data_points: projectDataPoints
            }
        };

        console.log('📁 Creating project in existing use case:', projectData);

        const response = await fetch('/api/aasx-etl/projects', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(projectData)
        });

        if (response.ok) {
            const result = await response.json();
            this.showSuccess(`Project "${projectName}" created successfully!`);
            this.closeModal();
            this.refreshDataManager();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create project');
        }
    }

    async createNewUseCaseWithProject() {
        // Collect use case data
        const useCaseData = {
            name: $('#newUseCaseName').val().trim(),
            description: $('#newUseCaseDescription').val().trim(),
            category: $('#newUseCaseCategory').val(),
            metadata: {
                industry: $('#newUseCaseIndustry').val() || null,
                complexity: $('#newUseCaseComplexity').val() || null,
                expected_duration: $('#newUseCaseDuration').val() || null,
                data_points: $('#newUseCaseDataPoints').val() ? parseInt($('#newUseCaseDataPoints').val()) : null,
                physics_type: $('#newUseCasePhysicsType').val() || null,
                tags: this.parseTags($('#newUseCaseTags').val()),
                famous_examples: this.parseLines($('#newUseCaseFamousExamples').val()),
                optimization_targets: [],
                materials: []
            }
        };

        // Collect project data
        const projectData = {
            name: $('#newProjectName').val().trim(),
            description: $('#newProjectDescription').val().trim(),
            tags: this.parseTags($('#newProjectTags').val()),
            metadata: {
                industry: $('#newProjectIndustry').val() || null,
                complexity: $('#newProjectComplexity').val() || null,
                expected_duration: $('#newProjectDuration').val() || null,
                data_points: $('#newProjectDataPoints').val() ? parseInt($('#newProjectDataPoints').val()) : null
            }
        };

        // Validate required fields
        if (!useCaseData.name || !useCaseData.description || !useCaseData.category || !projectData.name) {
            throw new Error('Use case name, description, category, and project name are required');
        }

        console.log('📋 Creating new use case with project:', { useCaseData, projectData });

        // Step 1: Create use case
        const useCaseResponse = await fetch('/api/aasx-etl/use-cases', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(useCaseData)
        });

        if (!useCaseResponse.ok) {
            const error = await useCaseResponse.json();
            throw new Error(error.detail || 'Failed to create use case');
        }

        const useCaseResult = await useCaseResponse.json();
        const useCaseId = useCaseResult.use_case_id;

        console.log('✅ Use case created:', useCaseId);

        // Step 2: Create project in the new use case
        projectData.use_case_id = useCaseId;

        const projectResponse = await fetch('/api/aasx-etl/projects', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(projectData)
        });

        if (projectResponse.ok) {
            const projectResult = await projectResponse.json();
            this.showSuccess(`Use case "${useCaseData.name}" and project "${projectData.name}" created successfully!`);
            this.closeModal();
            this.refreshDataManager();
        } else {
            const error = await projectResponse.json();
            throw new Error(error.detail || 'Failed to create project');
        }
    }

    parseTags(tagsString) {
        if (!tagsString || !tagsString.trim()) return [];
        return tagsString.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
    }

    parseLines(text) {
        if (!text || !text.trim()) return [];
        return text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    }

    showSuccess(message) {
        // Create a Bootstrap toast or alert
        const toastHtml = `
            <div class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-check-circle me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Add toast to page if toast container doesn't exist
        if ($('#toastContainer').length === 0) {
            $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
        }
        
        $('#toastContainer').append(toastHtml);
        const toast = new bootstrap.Toast($('#toastContainer .toast:last'));
        toast.show();
    }

    showError(message) {
        // Create a Bootstrap toast or alert
        const toastHtml = `
            <div class="toast align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Add toast to page if toast container doesn't exist
        if ($('#toastContainer').length === 0) {
            $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
        }
        
        $('#toastContainer').append(toastHtml);
        const toast = new bootstrap.Toast($('#toastContainer .toast:last'));
        toast.show();
    }

    closeModal() {
        const modal = bootstrap.Modal.getInstance($('#projectCreationModal'));
        if (modal) {
            modal.hide();
        }
    }

    refreshDataManager() {
        // Refresh the data manager to show new project/use case
        if (window.dataManager && typeof window.dataManager.loadProjects === 'function') {
            window.dataManager.loadProjects();
        }
        
        // Refresh dropdown manager if it exists
        if (window.dropdownManager && typeof window.dropdownManager.loadUseCases === 'function') {
            window.dropdownManager.loadUseCases();
        }
    }

    destroy() {
        // Clean up event listeners
        $('#existingUseCaseOption').off('click');
        $('#newUseCaseOption').off('click');
        $('#createProjectBtn').off('click');
        $('#projectCreationModal').off('show.bs.modal hidden.bs.modal');
        
        this.isInitialized = false;
        console.log('🧹 Project Creator destroyed');
    }
}

// Export for use in other modules
window.ProjectCreator = ProjectCreator;

// Auto-initialize when DOM is ready
$(document).ready(function() {
    if (!window.projectCreator) {
        window.projectCreator = new ProjectCreator();
    }
});

export default ProjectCreator; 