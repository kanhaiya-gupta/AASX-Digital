/**
 * Data Management Component
 * Handles import/export operations with dropdown selection from centralized database
 * Now with full authentication integration for user-specific data
 */

class DataManagementComponent {
    constructor() {
        this.apiBaseUrl = '/api/kg-neo4j';
        this.currentUseCase = null;
        this.currentProject = null;
        this.currentFile = null;
        
        // 🔐 Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.organizationId = null;
        
        // Track loading state to prevent duplicates
        this.projectsLoaded = false;
        
        // 🔐 Wait for authentication before initializing
        this.waitForAuthAndInit();
    }

    /**
     * 🔐 Wait for authentication system to be ready before initializing
     */
    async waitForAuthAndInit() {
        console.log('🔐 DataManagement: Waiting for authentication system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 DataManagement: Auth system already ready');
            this.init();
        } else {
            console.log('🔐 DataManagement: Waiting for auth system ready event...');
            window.addEventListener('authSystemReady', () => {
                console.log('🚀 DataManagement: Auth system ready, initializing...');
                this.init();
            });
        }
    }

    async init() {
        // 🔐 Update authentication state
        this.updateAuthState();
        
        // 🔐 Setup authentication event listeners
        this.setupAuthEventListeners();
        
        // Load user-specific data
        await this.loadUseCases();
        this.bindEvents();
        this.updateUI();
    }

    /**
     * 🔐 Update authentication state from global auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ DataManagement: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 DataManagement: Auth state update:', sessionInfo);
            
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            this.organizationId = sessionInfo.user?.organization_id;
            
            console.log(`🔐 DataManagement: User ${this.currentUser?.username || 'unauthenticated'} (org: ${this.organizationId || 'none'})`);
            
        } catch (error) {
            console.warn('⚠️ DataManagement: Error updating auth state:', error);
        }
    }

    /**
     * 🔐 Setup authentication event listeners
     */
    setupAuthEventListeners() {
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 DataManagement: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        window.addEventListener('logout', () => {
            console.log('🔐 DataManagement: Logout detected');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
    }

    /**
     * 🔐 Handle authentication state changes
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.organizationId) {
            console.log(`🔐 DataManagement: User authenticated, reloading data for ${this.currentUser.username}`);
            // Reload data for the authenticated user
            this.loadUseCases();
        } else {
            console.log('🔐 DataManagement: User not authenticated, clearing data');
            // Clear data and show demo/empty state
            this.clearData();
        }
    }

    /**
     * 🔐 Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = window.authManager?.getStoredToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            console.log(`🔐 DataManagement: Making authenticated API call for user ${this.currentUser?.username || 'unknown'}`);
        } else {
            console.log('🔐 DataManagement: Making unauthenticated API call');
        }
        
        return headers;
    }

    /**
     * 🔐 Clear data when user is not authenticated
     */
    clearData() {
        console.log('🔐 DataManagement: Clearing data for unauthenticated user');
        this.currentUseCase = null;
        this.currentProject = null;
        this.currentFile = null;
        
        // Clear ONLY Knowledge Graph specific dropdowns
        $('#use-case-select').empty().append('<option value="">Select Use Case...</option>').prop('disabled', true);
        $('#project-select').empty().append('<option value="">Select Project...</option>').prop('disabled', true);
        $('#file-select').empty().append('<option value="">Select File...</option>').prop('disabled', true);
        
        this.updateUI();
    }

    bindEvents() {
        // Use case selection - ONLY for Knowledge Graph specific dropdowns
        $('#use-case-select').on('change', (e) => {
            const useCaseId = $(e.target).val();
            console.log('🔍 DataManagement: Use case changed to:', useCaseId);
            this.onUseCaseChange(useCaseId, $(e.target).closest('.dropdown-section'));
        });

        // Project selection - ONLY for Knowledge Graph specific dropdowns
        $('#project-select').on('change', (e) => {
            const projectId = $(e.target).val();
            console.log('🔍 DataManagement: Project changed to:', projectId);
            this.onProjectChange(projectId, $(e.target).closest('.dropdown-section'));
        });

        // File selection - ONLY for Knowledge Graph specific dropdowns
        $('#file-select').on('change', (e) => {
            const fileId = $(e.target).val();
            console.log('🔍 DataManagement: File changed to:', fileId);
            this.currentFile = fileId;
            this.updateUI();
            
            // Load graph data for the selected file
            if (fileId) {
                this.loadGraphDataForFile(fileId);
            }
        });

        // Import button
        document.getElementById('import-data-btn')?.addEventListener('click', () => {
            this.importData();
        });

        // Export button
        document.getElementById('export-data-btn')?.addEventListener('click', () => {
            this.exportData();
        });

        // Import all files in project
        document.getElementById('import-project-btn')?.addEventListener('click', () => {
            this.importProject();
        });
    }

    async loadUseCases() {
        try {
            // 🔐 Use centralized AASX API for use cases (same as AASX module)
            const aasxApiUrl = '/api/aasx-etl/use-cases';
            console.log('🔍 DataManagement: Loading use cases from centralized AASX API:', aasxApiUrl);
            
            const response = await fetch(aasxApiUrl, { 
                headers: this.getAuthHeaders() 
            });
            const data = await response.json();
            console.log('📊 DataManagement: Use cases response:', data);
            
            // Handle both direct array response and success-wrapped response
            if (Array.isArray(data)) {
                console.log('✅ DataManagement: Populating dropdown with', data.length, 'use cases (direct array)');
                this.populateUseCaseDropdown(data);
            } else if (data.success && Array.isArray(data.use_cases)) {
                console.log('✅ DataManagement: Populating dropdown with', data.use_cases.length, 'use cases (success-wrapped)');
                this.populateUseCaseDropdown(data.use_cases);
            } else {
                console.error('❌ DataManagement: Failed to load use cases - invalid response format:', data);
                this.showError('Failed to load use cases - invalid response format');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading use cases:', error);
            this.showError('Error loading use cases');
        }
    }



    async onUseCaseChange(useCaseId, container) {
        this.currentUseCase = useCaseId;
        
        // Reset loading state for new use case
        this.projectsLoaded = false;
        
        // Reset project selection - ONLY Knowledge Graph specific dropdown
        const $projectSelect = $('#project-select');
        $projectSelect.val('');
        
        // Reset file selection - ONLY Knowledge Graph specific dropdown
        const $fileSelect = $('#file-select');
        $fileSelect.val('');
        
        if (useCaseId) {
            await this.loadProjects(useCaseId, container);
        } else {
            $projectSelect.empty();
            $projectSelect.append('<option value="">Select Project...</option>');
            $projectSelect.prop('disabled', true);
            
            $fileSelect.empty();
            $fileSelect.append('<option value="">Select File...</option>');
            $fileSelect.prop('disabled', true);
        }
        
        this.updateUI();
    }

    async onProjectChange(projectId, container) {
        this.currentProject = projectId;
        
        // Reset file selection - ONLY Knowledge Graph specific dropdown
        const $fileSelect = $('#file-select');
        $fileSelect.val('');
        
        if (projectId) {
            await this.loadFiles(projectId, container);
        } else {
            $fileSelect.empty();
            $fileSelect.append('<option value="">Select File...</option>');
            $fileSelect.prop('disabled', true);
        }
        
        this.updateUI();
    }

    async loadProjects(useCaseId, container) {
        // Prevent duplicate loading for the same use case
        if (this.currentUseCase === useCaseId && this.projectsLoaded) {
            console.log('🔍 DataManagement: Projects already loaded for use case:', useCaseId, 'skipping duplicate load');
            return;
        }
        
        try {
            // 🔐 Use centralized AASX API for projects (same as AASX module)
            const aasxApiUrl = `/api/aasx-etl/use-cases/${useCaseId}/projects`;
            console.log('🔍 DataManagement: Loading projects for use case:', useCaseId, 'from centralized AASX API:', aasxApiUrl);
            
            const response = await fetch(aasxApiUrl, { 
                headers: this.getAuthHeaders() 
            });
            const data = await response.json();
            console.log('📊 DataManagement: Projects response:', data);
            console.log('🔍 DataManagement: Sample project structure:', data[0] || 'No projects');
            
            // Handle both direct array response and success-wrapped response
            if (Array.isArray(data)) {
                console.log('✅ DataManagement: Populating project dropdown with', data.length, 'projects (direct array)');
                this.populateProjectDropdown(data, container);
                this.projectsLoaded = true;
            } else if (data.success && Array.isArray(data.projects)) {
                console.log('✅ DataManagement: Populating project dropdown with', data.projects.length, 'projects (success-wrapped)');
                this.populateProjectDropdown(data.projects, container);
                this.projectsLoaded = true;
            } else {
                console.error('❌ DataManagement: Failed to load projects - invalid response format:', data);
                this.showError('Failed to load projects - invalid response format');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading projects:', error);
            this.showError('Error loading projects');
        }
    }

    async loadFiles(projectId, container) {
        try {
            // 🔐 Use centralized AASX API for project files (same as AASX module)
            const aasxApiUrl = `/api/aasx-etl/projects/${projectId}/files`;
            console.log('🔍 DataManagement: Loading files for project:', projectId, 'from centralized AASX API:', aasxApiUrl);
            
            const response = await fetch(aasxApiUrl, { 
                headers: this.getAuthHeaders() 
            });
            const data = await response.json();
            console.log('📊 DataManagement: Files response:', data);
            
            // Handle different response formats
            if (Array.isArray(data)) {
                // Direct array response
                if (data.length === 0) {
                    console.log('⚠️ DataManagement: No files found for project, showing empty state');
                    this.populateFileDropdown([], container, true); // true = show empty state
                } else {
                    console.log('✅ DataManagement: Populating file dropdown with', data.length, 'files (direct array)');
                    this.populateFileDropdown(data, container);
                }
            } else if (data.files && Array.isArray(data.files)) {
                // Object with files array (our new endpoint format)
                if (data.files.length === 0) {
                    console.log('⚠️ DataManagement: No files found for project, showing empty state');
                    this.populateFileDropdown([], container, true); // true = show empty state
                } else {
                    console.log('✅ DataManagement: Populating file dropdown with', data.files.length, 'files (object format)');
                    this.populateFileDropdown(data.files, container);
                }
            } else if (data.success && Array.isArray(data.files)) {
                // Success-wrapped response
                if (data.files.length === 0) {
                    console.log('⚠️ DataManagement: No files found for project, showing empty state');
                    this.populateFileDropdown([], container, true); // true = show empty state
                } else {
                    console.log('✅ DataManagement: Populating file dropdown with', data.files.length, 'files (success-wrapped)');
                    this.populateFileDropdown(data.files, container);
                }
            } else if (data.detail === 'Not Found') {
                // Handle 404 case - project has no files yet
                console.log('⚠️ DataManagement: Project has no files yet (404)');
                this.populateFileDropdown([], container, true); // true = show empty state
            } else {
                console.error('❌ DataManagement: Failed to load files - invalid response format:', data);
                this.showError('Failed to load files - invalid response format');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading files:', error);
            this.showError('Error loading files');
        }
    }

    populateUseCaseDropdown(useCases) {
        console.log('🔍 DataManagement: populateUseCaseDropdown called with:', useCases);
        const select = document.getElementById('use-case-select');
        if (!select) {
            console.error('❌ DataManagement: use-case-select element not found');
            return;
        }

        console.log('✅ DataManagement: Found use-case-select element, populating...');
        select.innerHTML = '<option value="">Select Use Case...</option>';
        useCases.forEach(useCase => {
            // Handle both use_case_name/use_case_id and name/id structures
            const useCaseName = useCase.use_case_name || useCase.name || 'Unnamed Use Case';
            const useCaseId = useCase.use_case_id || useCase.id || useCase.useCaseId;
            console.log('🔍 DataManagement: Adding use case:', useCaseName, 'with ID:', useCaseId);
            const option = document.createElement('option');
            option.value = useCaseId;
            option.textContent = useCaseName;
            select.appendChild(option);
        });
        console.log('✅ DataManagement: Dropdown populated with', useCases.length, 'use cases');
    }

    populateProjectDropdown(projects, container) {
        console.log('🔍 DataManagement: populateProjectDropdown called with:', projects);
        
        // ONLY target the Knowledge Graph specific project dropdown by ID
        const $select = $('#project-select');
        
        if (!$select.length) {
            console.error('❌ DataManagement: Knowledge Graph project-select element not found');
            return;
        }
        
        console.log('✅ DataManagement: Found Knowledge Graph project-select element, clearing and populating...');
        
        // Clear existing options completely
        $select.empty();
        $select.append('<option value="">Select Project...</option>');
        $select.prop('disabled', false);
        
        // Add new project options
        projects.forEach(project => {
            // Handle both project_name/project_id and name/id structures
            const projectName = project.project_name || project.name || 'Unnamed Project';
            const projectId = project.project_id || project.id || project.projectId;
            console.log('🔍 DataManagement: Adding project:', projectName, 'with ID:', projectId);
            $select.append(`<option value="${projectId}">${projectName}</option>`);
        });
        
        console.log('✅ DataManagement: Knowledge Graph project dropdown populated with', projects.length, 'projects');

        // Clear file dropdown
        this.clearFileDropdown(container);
    }

    populateFileDropdown(files, container, showEmptyState = false) {
        console.log('🔍 DataManagement: populateFileDropdown called with:', files, 'showEmptyState:', showEmptyState);
        const $select = container.find('.file-select');
        
        console.log('✅ DataManagement: Found file-select element, populating...');
        $select.empty();
        
        if (showEmptyState || files.length === 0) {
            $select.append('<option value="">No files available</option>');
            $select.prop('disabled', true);
            console.log('⚠️ DataManagement: File dropdown shows no files available');
        } else {
            $select.append('<option value="">Select File...</option>');
            $select.prop('disabled', false);
            
            files.forEach(file => {
                console.log('🔍 DataManagement: Adding file:', file.filename, 'with ID:', file.file_id);
                $select.append(`<option value="${file.file_id}">${file.filename}</option>`);
            });
            console.log('✅ DataManagement: File dropdown populated with', files.length, 'files');
        }
    }

    clearFileDropdown(container) {
        // ONLY target the Knowledge Graph specific file dropdown by ID
        const $select = $('#file-select');
        $select.empty();
        $select.append('<option value="">Select File...</option>');
        $select.prop('disabled', true);
        this.currentFile = null;
    }

    async importData() {
        if (!this.currentFile) {
            this.showError('Please select a file to import');
            return;
        }

        try {
            this.showLoading('Importing data...');
            
            const response = await fetch(`${this.apiBaseUrl}/import/file/${this.currentFile}`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            const data = await response.json();
            
            if (data.success) {
                const nodeCount = data.node_count || 0;
                const edgeCount = data.relationship_count || data.edges_count || 0;
                
                if (nodeCount > 0 || edgeCount > 0) {
                    this.showSuccess(`Successfully imported ${nodeCount} nodes and ${edgeCount} relationships`);
                } else {
                    this.showSuccess(`File processed successfully. Data is already available in the database.`);
                }
                
                // Store the graph data globally for visualization
                if (data.graph_data) {
                    window.kgGraphData = data.graph_data;
                    console.log('📊 Graph data stored for visualization:', data.graph_data);
                    
                    // Trigger graph visualization
                    this.triggerGraphVisualization(data.graph_data);
                } else {
                    // If no graph data in response, try to load it from the file
                    await this.loadGraphDataForFile(this.currentFile);
                }
                
                this.updateImportStatus();
            } else {
                this.showError(data.error || 'Import failed');
            }
        } catch (error) {
            console.error('Import error:', error);
            this.showError('Import failed');
        } finally {
            this.hideLoading();
        }
    }

    triggerGraphVisualization(graphData) {
        try {
            console.log('🎨 Triggering graph visualization with data:', graphData);
            
            // Import and call the visualization function
            import('./graph_visualization.js').then(module => {
                if (module.loadGraphDataFromImport) {
                    module.loadGraphDataFromImport(graphData);
                } else {
                    console.warn('Visualization module does not have loadGraphDataFromImport method');
                }
            }).catch(error => {
                console.error('Failed to load visualization module:', error);
            });
            
            // Also refresh analytics dashboard
            this.refreshAnalyticsDashboard();
        } catch (error) {
            console.error('Error triggering graph visualization:', error);
        }
    }
    
    async loadGraphDataForFile(fileId) {
        try {
            console.log('🔍 Loading graph data for file:', fileId);
            
            // First check if the file has graph data
            const checkResponse = await fetch(`${this.apiBaseUrl}/files/${fileId}/graph-exists`, { headers: this.getAuthHeaders() });
            const checkData = await checkResponse.json();
            
            if (checkData.exists) {
                // Load the graph data
                const response = await fetch(`${this.apiBaseUrl}/files/${fileId}/graph-data`, { headers: this.getAuthHeaders() });
                const data = await response.json();
                
                if (data.success && data.graph_data) {
                    console.log('📊 Loaded graph data for file:', data.graph_data);
                    
                    // Trigger graph visualization
                    this.triggerGraphVisualization(data.graph_data);
                } else {
                    console.log('📊 No graph data available for this file');
                    this.showGraphMessage("No graph data available for this file");
                }
            } else {
                console.log('📊 File does not have graph data yet');
                this.showGraphMessage("This file does not have graph data yet. Import it first to generate the graph.");
            }
        } catch (error) {
            console.error('Error loading graph data for file:', error);
            this.showGraphMessage("Error loading graph data");
        }
    }
    
    showGraphMessage(message) {
        // Import and call the visualization function to show message
        import('./graph_visualization.js').then(module => {
            if (module.showGraphMessage) {
                module.showGraphMessage(message);
            }
        }).catch(error => {
            console.error('Failed to load visualization module:', error);
        });
    }
    
    async refreshAnalyticsDashboard() {
        try {
            console.log('📊 Refreshing analytics dashboard...');
            const response = await fetch('/api/kg-neo4j/database-stats', { headers: this.getAuthHeaders() });
            const data = await response.json();
            
            if (data.success) {
                this.updateAnalyticsDisplay(data.stats);
            }
        } catch (error) {
            console.error('Failed to refresh analytics dashboard:', error);
        }
    }
    
    updateAnalyticsDisplay(stats) {
        const totalNodes = document.getElementById('total-nodes');
        const totalRelationships = document.getElementById('total-relationships');
        const totalLabels = document.getElementById('total-labels');
        const totalTypes = document.getElementById('total-types');
        
        if (totalNodes) totalNodes.textContent = stats.total_nodes || 0;
        if (totalRelationships) totalRelationships.textContent = stats.total_relationships || 0;
        if (totalLabels) totalLabels.textContent = stats.total_labels || 0;
        if (totalTypes) totalTypes.textContent = stats.total_relationship_types || 0;
        
        console.log('📊 Updated analytics dashboard:', stats);
    }

    async importProject() {
        if (!this.currentProject) {
            this.showError('Please select a project to import');
            return;
        }

        try {
            this.showLoading('Importing project data...');
            
            const response = await fetch(`${this.apiBaseUrl}/import/project/${this.currentProject}`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Successfully imported project with ${data.total_nodes} nodes and ${data.total_relationships} relationships`);
                this.updateImportStatus();
            } else {
                this.showError(data.error || 'Project import failed');
            }
        } catch (error) {
            console.error('Project import error:', error);
            this.showError('Project import failed');
        } finally {
            this.hideLoading();
        }
    }

    async exportData() {
        const format = document.getElementById('export-format-select')?.value || 'json';
        
        if (!this.currentFile && !this.currentProject) {
            this.showError('Please select a file or project to export');
            return;
        }

        try {
            this.showLoading('Preparing export...');
            
            const endpoint = this.currentFile 
                ? `${this.apiBaseUrl}/export/file/${this.currentFile}`
                : `${this.apiBaseUrl}/export/project/${this.currentProject}`;
            
            const response = await fetch(`${endpoint}?format=${format}`, { headers: this.getAuthHeaders() });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `graph_export.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccess('Export completed successfully');
            } else {
                const data = await response.json();
                this.showError(data.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Export failed');
        } finally {
            this.hideLoading();
        }
    }

    async updateImportStatus() {
        // Update the import status display
        try {
            const response = await fetch(`${this.apiBaseUrl}/import/status`, { headers: this.getAuthHeaders() });
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.status);
            }
        } catch (error) {
            console.error('Error updating import status:', error);
            // Provide fallback status if API fails
            this.updateStatusDisplay({
                total_files: 0,
                imported_files: 0,
                pending_files: 0
            });
        }
    }

    updateStatusDisplay(status) {
        const statusElement = document.getElementById('import-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-item">
                    <span class="status-label">Total Files:</span>
                    <span class="status-value">${status.total_files}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Imported:</span>
                    <span class="status-value">${status.imported_files}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Pending:</span>
                    <span class="status-value">${status.pending_files}</span>
                </div>
            `;
        }
    }

    updateUI() {
        // Enable/disable buttons based on selection
        const importBtn = document.getElementById('import-data-btn');
        const importProjectBtn = document.getElementById('import-project-btn');
        const exportBtn = document.getElementById('export-data-btn');

        if (importBtn) {
            importBtn.disabled = !this.currentFile;
        }
        if (importProjectBtn) {
            importProjectBtn.disabled = !this.currentProject;
        }
        if (exportBtn) {
            exportBtn.disabled = !this.currentFile && !this.currentProject;
        }

        // Update selection display
        this.updateSelectionDisplay();
    }

    updateSelectionDisplay() {
        const display = document.getElementById('selection-display');
        if (display) {
            let text = '';
            if (this.currentUseCase) {
                text += `Use Case: ${this.getUseCaseName(this.currentUseCase)}`;
            }
            if (this.currentProject) {
                text += text ? ` → Project: ${this.getProjectName(this.currentProject)}` : `Project: ${this.getProjectName(this.currentProject)}`;
            }
            if (this.currentFile) {
                text += text ? ` → File: ${this.getFileName(this.currentFile)}` : `File: ${this.getFileName(this.currentFile)}`;
            }
            
            display.textContent = text || 'No selection';
        }
    }

    getUseCaseName(id) {
        const select = document.getElementById('use-case-select');
        const option = select?.querySelector(`option[value="${id}"]`);
        return option?.textContent || id;
    }

    getProjectName(id) {
        const select = document.getElementById('project-select');
        const option = select?.querySelector(`option[value="${id}"]`);
        return option?.textContent || id;
    }

    getFileName(id) {
        const select = document.getElementById('file-select');
        const option = select?.querySelector(`option[value="${id}"]`);
        return option?.textContent || id;
    }

    showLoading(message) {
        const loadingElement = document.getElementById('loading-indicator');
        if (loadingElement) {
            loadingElement.textContent = message;
            loadingElement.style.display = 'block';
        }
    }

    hideLoading() {
        const loadingElement = document.getElementById('loading-indicator');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const container = document.querySelector('.data-management-container') || document.body;
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Export for modular usage
export default DataManagementComponent; 