/**
 * Data Management Component
 * Handles import/export operations with dropdown selection from centralized database
 */

class DataManagementComponent {
    constructor() {
        this.apiBaseUrl = '/api/kg-neo4j';
        this.currentUseCase = null;
        this.currentProject = null;
        this.currentFile = null;
        this.init();
    }

    init() {
        this.loadUseCases();
        this.bindEvents();
        this.updateUI();
    }

    bindEvents() {
        // Use case selection - using jQuery like AASX
        $('.use-case-select').on('change', (e) => {
            const useCaseId = $(e.target).val();
            console.log('🔍 DataManagement: Use case changed to:', useCaseId);
            this.onUseCaseChange(useCaseId, $(e.target).closest('.dropdown-section'));
        });

        // Project selection - using jQuery like AASX
        $('.project-select').on('change', (e) => {
            const projectId = $(e.target).val();
            console.log('🔍 DataManagement: Project changed to:', projectId);
            this.onProjectChange(projectId, $(e.target).closest('.dropdown-section'));
        });

        // File selection - using jQuery like AASX
        $('.file-select').on('change', (e) => {
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
            console.log('🔍 DataManagement: Loading use cases from:', `${this.apiBaseUrl}/use-cases`);
            const response = await fetch(`${this.apiBaseUrl}/use-cases`);
            const data = await response.json();
            console.log('📊 DataManagement: Use cases response:', data);
            
            if (data.success) {
                console.log('✅ DataManagement: Populating dropdown with', data.use_cases.length, 'use cases');
                this.populateUseCaseDropdown(data.use_cases);
            } else {
                console.error('❌ DataManagement: Failed to load use cases:', data);
                this.showError('Failed to load use cases');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading use cases:', error);
            this.showError('Error loading use cases');
        }
    }

    async loadProjects() {
        if (!this.currentUseCase) return;

        try {
            console.log('🔍 DataManagement: Loading projects for use case:', this.currentUseCase);
            const response = await fetch(`${this.apiBaseUrl}/use-cases/${this.currentUseCase}/projects`);
            const data = await response.json();
            console.log('📊 DataManagement: Projects response:', data);
            
            if (data.success) {
                console.log('✅ DataManagement: Populating project dropdown with', data.projects.length, 'projects');
                this.populateProjectDropdown(data.projects);
            } else {
                console.error('❌ DataManagement: Failed to load projects:', data);
                this.showError('Failed to load projects');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading projects:', error);
            this.showError('Error loading projects');
        }
    }

    async onUseCaseChange(useCaseId, container) {
        this.currentUseCase = useCaseId;
        
        // Reset project selection
        const $projectSelect = container.find('.project-select');
        $projectSelect.val('');
        
        // Reset file selection
        const $fileSelect = container.find('.file-select');
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
        
        // Reset file selection
        const $fileSelect = container.find('.file-select');
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
        try {
            console.log('🔍 DataManagement: Loading projects for use case:', useCaseId);
            const response = await fetch(`${this.apiBaseUrl}/use-cases/${useCaseId}/projects`);
            const data = await response.json();
            console.log('📊 DataManagement: Projects response:', data);
            
            if (data.success) {
                console.log('✅ DataManagement: Populating project dropdown with', data.projects.length, 'projects');
                this.populateProjectDropdown(data.projects, container);
            } else {
                console.error('❌ DataManagement: Failed to load projects:', data);
                this.showError('Failed to load projects');
            }
        } catch (error) {
            console.error('❌ DataManagement: Error loading projects:', error);
            this.showError('Error loading projects');
        }
    }

    async loadFiles(projectId, container) {
        try {
            console.log('🔍 DataManagement: Loading files for project:', projectId);
            const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/files`);
            const data = await response.json();
            console.log('📊 DataManagement: Files response:', data);
            
            if (data.success) {
                console.log('✅ DataManagement: Populating file dropdown with', data.files.length, 'files');
                this.populateFileDropdown(data.files, container);
            } else {
                console.error('❌ DataManagement: Failed to load files:', data);
                this.showError('Failed to load files');
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
            console.log('🔍 DataManagement: Adding use case:', useCase.use_case_name, 'with ID:', useCase.use_case_id);
            const option = document.createElement('option');
            option.value = useCase.use_case_id;
            option.textContent = useCase.use_case_name;
            select.appendChild(option);
        });
        console.log('✅ DataManagement: Dropdown populated with', useCases.length, 'use cases');
    }

    populateProjectDropdown(projects, container) {
        console.log('🔍 DataManagement: populateProjectDropdown called with:', projects);
        const $select = container.find('.project-select');
        
        console.log('✅ DataManagement: Found project-select element, populating...');
        $select.empty();
        $select.append('<option value="">Select Project...</option>');
        $select.prop('disabled', false);
        
        projects.forEach(project => {
            console.log('🔍 DataManagement: Adding project:', project.project_name, 'with ID:', project.project_id);
            $select.append(`<option value="${project.project_id}">${project.project_name}</option>`);
        });
        console.log('✅ DataManagement: Project dropdown populated with', projects.length, 'projects');

        // Clear file dropdown
        this.clearFileDropdown(container);
    }

    populateFileDropdown(files, container) {
        console.log('🔍 DataManagement: populateFileDropdown called with:', files);
        const $select = container.find('.file-select');
        
        console.log('✅ DataManagement: Found file-select element, populating...');
        $select.empty();
        $select.append('<option value="">Select File...</option>');
        $select.prop('disabled', false);
        
        files.forEach(file => {
            console.log('🔍 DataManagement: Adding file:', file.filename, 'with ID:', file.file_id);
            $select.append(`<option value="${file.file_id}">${file.filename}</option>`);
        });
        console.log('✅ DataManagement: File dropdown populated with', files.length, 'files');
    }

    clearFileDropdown(container) {
        const $select = container.find('.file-select');
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
                headers: {
                    'Content-Type': 'application/json'
                }
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
            const checkResponse = await fetch(`${this.apiBaseUrl}/files/${fileId}/graph-exists`);
            const checkData = await checkResponse.json();
            
            if (checkData.exists) {
                // Load the graph data
                const response = await fetch(`${this.apiBaseUrl}/files/${fileId}/graph-data`);
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
            const response = await fetch('/api/kg-neo4j/database-stats');
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
                headers: {
                    'Content-Type': 'application/json'
                }
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
            
            const response = await fetch(`${endpoint}?format=${format}`);
            
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
            const response = await fetch(`${this.apiBaseUrl}/import/status`);
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