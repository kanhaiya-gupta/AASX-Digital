/**
 * Project Manager JavaScript
 * 
 * Handles project management functionality including:
 * - Project creation, viewing, and deletion
 * - File upload and management
 * - Project categorization by use cases
 * - Project statistics and organization
 */

console.log('🚀 project_manager.js loaded successfully');

class ProjectManager {
    constructor() {
        this.projects = [];
        this.useCases = {};
        this.currentProject = null;
    }

    async init() {
        try {
            console.log('🚀 Project Manager initializing...');
            
            // Initialize flow chart
            this.initFlowChart();
            
            // Load projects
            await this.loadProjects();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Update stats
            await this.updateStats();
            
            // Set up auto-refresh
            this.autoRefresh();
            
            console.log('✅ Project Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Project Manager:', error);
        }
    }

    setupEventListeners() {
        // Project creation modal
        $('#createProjectBtn').on('click', () => this.showCreateProjectModal());
        $('#createProjectForm').on('submit', (e) => {
            e.preventDefault();
            this.createProject();
        });
        $('#resetCreateProjectBtn').on('click', () => this.resetCreateProjectForm());

        // Hierarchical selection for file upload
        $('#uploadUseCaseSelect').on('change', () => this.onUseCaseChange('upload'));
        $('#urlUseCaseSelect').on('change', () => this.onUseCaseChange('url'));
        
        // Hierarchical selection for ETL pipeline
        $('#etlUseCaseSelect').on('change', () => this.onUseCaseChange('etl'));

        // File upload
        $('#fileUploadForm').on('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload(e);
        });
        $('#urlUploadForm').on('submit', (e) => {
            e.preventDefault();
            this.handleUrlUpload(e);
        });

        // Project management
        $('#refreshProjectsBtn').on('click', () => this.refreshAndSync());
        $('#manageProjectSelect').on('change', () => this.onManageProjectChange());
        $('#manageFileSelect').on('change', () => this.onManageFileChange());

        // Pipeline integration
        $('#pipelineProjectSelect').on('change', () => this.onPipelineProjectChange());
        $('#pipelineModeSelect').on('change', () => this.onPipelineModeChange());

        // Action buttons
        $('#viewProjectBtn').on('click', () => this.viewSelectedProject());
        $('#deleteProjectBtn').on('click', () => this.deleteSelectedProject());
        $('#viewFileBtn').on('click', () => this.viewSelectedFile());
        $('#deleteFileBtn').on('click', () => this.deleteSelectedFile());
        $('#processFileBtn').on('click', () => this.processSelectedFile());

        // Auto-refresh
        setInterval(() => this.autoRefresh(), 30000); // Refresh every 30 seconds
    }

    async loadProjects() {
        try {
            console.log('🔄 Loading projects and use cases...');
            
            // Load both projects and use cases
            const [projectsResponse, useCasesResponse] = await Promise.all([
                fetch('/aasx/api/projects'),
                fetch('/physics-modeling/api/use-cases')
            ]);
            
            console.log('📡 Projects response status:', projectsResponse.status);
            console.log('📡 Use cases response status:', useCasesResponse.status);
            
            if (projectsResponse.ok && useCasesResponse.ok) {
                this.projects = await projectsResponse.json();
                const useCasesData = await useCasesResponse.json();
                
                // Store use cases for project categorization
                this.useCases = useCasesData.use_cases || {};
                
                console.log('📦 Loaded projects:', this.projects.length);
                console.log('📋 Loaded use cases:', Object.keys(this.useCases).length);
                
                // Debug: Log first few projects to see their structure
                if (this.projects.length > 0) {
                    console.log('🔍 Sample project structure:', this.projects[0]);
                }
                
                this.renderProjects();
                this.updateProjectSelects();
                await this.updateStats();
                
                // Debug: Check if stats elements exist
                console.log('🔍 Checking stats elements:');
                console.log('totalProjects element:', $('#totalProjects').length);
                console.log('totalFiles element:', $('#totalFiles').length);
                console.log('totalSize element:', $('#totalSize').length);
                console.log('processedFiles element:', $('#processedFiles').length);
            } else {
                console.error('❌ Failed to load data:', {
                    projects: projectsResponse.status,
                    useCases: useCasesResponse.status
                });
                
                // Try to load just projects if use cases fail
                if (projectsResponse.ok) {
                    this.projects = await projectsResponse.json();
                    console.log('📦 Loaded projects only:', this.projects.length);
                    this.renderProjects();
                    this.updateProjectSelects();
                    await this.updateStats();
                }
            }
        } catch (error) {
            console.error('❌ Error loading projects:', error);
        }
    }

    renderProjects() {
        const projectsList = $('#projectsList');
        
        if (!this.projects || this.projects.length === 0) {
            projectsList.html(`
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">No Projects Found</h4>
                    <p class="text-muted mb-4">Get started by creating your first project to organize your AASX files and analysis workflows.</p>
                    <button class="btn btn-success" onclick="projectManager.showCreateProjectModal()">
                        <i class="fas fa-plus"></i>
                        Create First Project
                    </button>
                </div>
            `);
            return;
        }

        // Group projects by use case categories
        const projectCategories = this.groupProjectsByCategory();
        
        // Render categorized projects with a clean header
        const categoriesHtml = Object.entries(projectCategories).map(([category, projects]) => 
            this.renderProjectCategory(category, projects)
        ).join('');

        projectsList.html(`
            <div class="project-categories">
                ${categoriesHtml}
            </div>
        `);
    }

    groupProjectsByCategory() {
        console.log('📋 Categorizing projects by physics type...');
        
        const categories = {
            'thermal': { name: 'Thermal Analysis', projects: [] },
            'structural': { name: 'Structural Analysis', projects: [] },
            'fluid_dynamics': { name: 'Fluid Dynamics Analysis', projects: [] },
            'multi_physics': { name: 'Multi-Physics Analysis', projects: [] },
            'industrial': { name: 'Industrial Applications Analysis', projects: [] },
            'other': { name: 'Other Projects Analysis', projects: [] }
        };
        
        // Track processed projects to avoid duplication
        const processedProjects = new Set();
        
        this.projects.forEach(project => {
            // Skip if already processed
            if (processedProjects.has(project.project_id)) {
                return;
            }
            
            let category = null;
            
            // Check metadata first
            if (project.metadata && project.metadata.physics_type) {
                const physicsType = project.metadata.physics_type.toLowerCase();
                
                // Map physics types to categories
                if (physicsType === 'thermal') {
                    category = 'thermal';
                } else if (physicsType === 'structural') {
                    category = 'structural';
                } else if (physicsType === 'fluid_dynamics' || physicsType === 'fluid-dynamics') {
                    category = 'fluid_dynamics';
                } else if (physicsType === 'multi_physics' || physicsType === 'multi-physics') {
                    category = 'multi_physics';
                } else if (physicsType === 'industrial') {
                    category = 'industrial';
                } else {
                    category = 'other';
                }
            }
            // Check tags if no metadata
            else if (project.tags && Array.isArray(project.tags)) {
                const tags = project.tags.map(tag => tag.toLowerCase());
                
                if (tags.some(tag => tag.includes('thermal'))) {
                    category = 'thermal';
                } else if (tags.some(tag => tag.includes('structural'))) {
                    category = 'structural';
                } else if (tags.some(tag => tag.includes('fluid') || tag.includes('aerodynamic'))) {
                    category = 'fluid_dynamics';
                } else if (tags.some(tag => tag.includes('multi') || tag.includes('coupling'))) {
                    category = 'multi_physics';
                } else if (tags.some(tag => tag.includes('industrial') || tag.includes('manufacturing'))) {
                    category = 'industrial';
                } else {
                    category = 'other';
                }
            }
            // Default to other if no classification found
            else {
                category = 'other';
            }
            
            if (category && categories[category]) {
                categories[category].projects.push(project);
                processedProjects.add(project.project_id);
                console.log(`📁 Added project "${project.name}" to category "${category}" (physics_type: ${project.metadata?.physics_type || 'none'})`);
            }
        });
        
        console.log('📊 Project categorization results:');
        Object.entries(categories).forEach(([key, data]) => {
            console.log(`  ${data.name}: ${data.projects.length} projects`);
        });
        
        return categories;
    }

    renderProjectCard(project) {
        const fileCount = project.file_count || 0;
        const totalSize = this.formatFileSize(project.total_size || 0);
        const createdDate = new Date(project.created_at).toLocaleDateString();
        
        // Get project metadata for display
        const metadata = project.metadata || {};
        const industry = metadata.industry || 'N/A';
        const physicsType = metadata.physics_type || 'N/A';
        const complexity = metadata.complexity || 'N/A';
        
        // Create metadata info section
        const metadataInfo = `
            <div class="mb-2">
                <small class="text-primary">
                    <i class="fas fa-industry"></i>
                    <strong>Industry:</strong> ${industry}
                </small>
            </div>
            <div class="mb-2">
                <small class="text-info">
                    <i class="fas fa-cogs"></i>
                    <strong>Physics Type:</strong> ${physicsType.replace('_', ' ').toUpperCase()}
                </small>
            </div>
            <div class="mb-2">
                <small class="text-muted">
                    <i class="fas fa-signal"></i>
                    <strong>Complexity:</strong> ${complexity.replace('_', ' ').toUpperCase()}
                </small>
            </div>
        `;
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 border-success">
                    <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-folder"></i>
                            ${project.name}
                        </h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="projectManager.viewProject('${project.project_id}')">
                                    <i class="fas fa-eye text-primary"></i> View Details
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="projectManager.uploadToProject('${project.project_id}')">
                                    <i class="fas fa-upload text-info"></i> Upload File
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="projectManager.deleteProject('${project.project_id}')">
                                    <i class="fas fa-trash"></i> Delete Project
                                </a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="card-body">
                        ${metadataInfo}
                        
                        <div class="row text-center">
                            <div class="col-6">
                                <h6 class="text-success">${fileCount}</h6>
                                <small class="text-muted">Files</small>
                            </div>
                            <div class="col-6">
                                <h6 class="text-info">${totalSize}</h6>
                                <small class="text-muted">Size</small>
                            </div>
                        </div>
                        <div class="mt-2">
                            ${project.tags && project.tags.length > 0 ? 
                                project.tags.filter(tag => !tag.startsWith('use-case-')).map(tag => 
                                    `<span class="badge bg-secondary me-1">${tag}</span>`
                                ).join('') : 
                                '<span class="text-muted">No tags</span>'
                            }
                        </div>
                    </div>
                    <div class="card-footer text-muted">
                        <small>Created: ${createdDate}</small>
                    </div>
                </div>
            </div>
        `;
    }

    renderProjectCategory(categoryKey, categoryData) {
        // Define category configurations
        const categoryConfigs = {
            'thermal': { 
                name: 'Thermal Analysis', 
                icon: 'fas fa-fire', 
                color: 'text-danger', 
                description: 'Heat transfer, thermal management, and temperature analysis for electronics, engines, and industrial processes',
                examples: 'CPU cooling, battery thermal management, solar panels, aerospace thermal protection'
            },
            'structural': { 
                name: 'Structural Analysis', 
                icon: 'fas fa-cube', 
                color: 'text-warning', 
                description: 'Stress analysis, deformation, and structural integrity for mechanical components and systems',
                examples: 'Bridge design, aircraft wings, pressure vessels, automotive chassis'
            },
            'fluid_dynamics': { 
                name: 'Fluid Dynamics Analysis', 
                icon: 'fas fa-water', 
                color: 'text-info', 
                description: 'Fluid flow, aerodynamics, and hydrodynamic analysis for optimal performance',
                examples: 'Aircraft aerodynamics, automotive design, wind turbines, marine vessels'
            },
            'multi_physics': { 
                name: 'Multi-Physics Analysis', 
                icon: 'fas fa-link', 
                color: 'text-success', 
                description: 'Complex interactions between multiple physical phenomena and coupled systems',
                examples: 'Fluid-structure interaction, thermal-structural coupling, electrochemical systems'
            },
            'industrial': { 
                name: 'Industrial Applications Analysis', 
                icon: 'fas fa-industry', 
                color: 'text-secondary', 
                description: 'Manufacturing processes, industrial systems, and infrastructure optimization',
                examples: 'Additive manufacturing, chemical reactors, power plants, hydrogen infrastructure'
            },
            'other': { 
                name: 'Other Projects Analysis', 
                icon: 'fas fa-folder', 
                color: 'text-muted', 
                description: 'General projects and miscellaneous analysis categories',
                examples: 'Research projects, custom analysis, experimental setups'
            }
        };
        
        const config = categoryConfigs[categoryKey] || categoryConfigs['other'];
        const projectCount = categoryData.projects.length;
        const categoryId = `category-${categoryKey}`;
        
        const projectsHtml = categoryData.projects.map(project => this.renderProjectCard(project)).join('');
        
        return `
            <div class="category-card mb-4">
                <div class="category-header" data-bs-toggle="collapse" data-bs-target="#${categoryId}" 
                     aria-expanded="false" aria-controls="${categoryId}">
                    <div class="category-content">
                        <div class="category-icon">
                            <i class="${config.icon} ${config.color}"></i>
                        </div>
                        <div class="category-info">
                            <h3 class="category-title">${config.name}</h3>
                            <p class="category-description">${config.description}</p>
                            <div class="category-examples">
                                <span class="examples-label">Examples:</span>
                                <span class="examples-text">${config.examples}</span>
                            </div>
                        </div>
                        <div class="category-actions">
                            <div class="project-count">
                                <span class="count-number">${projectCount}</span>
                                <span class="count-label">Projects</span>
                            </div>
                            <div class="expand-indicator">
                                <i class="fas fa-chevron-down"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="collapse" id="${categoryId}">
                    <div class="category-projects">
                        <div class="row">
                            ${projectsHtml}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateProjectSelects() {
        const projectSelects = ['#pipelineProjectSelect', '#manageProjectSelect'];
        
        projectSelects.forEach(selectId => {
            const select = $(selectId);
            if (select.length > 0) {
                select.empty();
                select.append('<option value="">Select a project...</option>');
                
                this.projects.forEach(project => {
                    select.append(`<option value="${project.project_id}">${project.name}</option>`);
                });
            }
        });
    }

    onUseCaseChange(context) {
        const useCaseSelect = $(`#${context}UseCaseSelect`);
        const projectSelect = $(`#${context}ProjectSelect`);
        const selectedUseCase = useCaseSelect.val();
        
        // Reset project select
        projectSelect.empty();
        projectSelect.append('<option value="">Choose a project...</option>');
        
        if (selectedUseCase) {
            // Filter projects by use case
            const filteredProjects = this.projects.filter(project => {
                // Check if project has metadata with physics_type
                if (project.metadata && project.metadata.physics_type) {
                    return project.metadata.physics_type.toLowerCase() === selectedUseCase.toLowerCase();
                }
                // Check tags for use case
                if (project.tags && Array.isArray(project.tags)) {
                    return project.tags.some(tag => 
                        tag.toLowerCase().includes(selectedUseCase.toLowerCase()) ||
                        tag.toLowerCase().includes(selectedUseCase.replace('_', ' ').toLowerCase())
                    );
                }
                return false;
            });
            
            // Populate project select with filtered projects
            filteredProjects.forEach(project => {
                projectSelect.append(`<option value="${project.project_id}">${project.name}</option>`);
            });
            
            // Enable project select
            projectSelect.prop('disabled', false);
            
            console.log(`📋 Found ${filteredProjects.length} projects for use case: ${selectedUseCase}`);
        } else {
            // Disable project select if no use case selected
            projectSelect.prop('disabled', true);
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/aasx/api/stats');
            if (response.ok) {
                const stats = await response.json();
                
                // Update main dashboard stats
                $('#totalProjects').text(stats.total_projects || 0);
                $('#totalFiles').text(stats.total_files || 0);
                $('#totalSize').text(this.formatFileSize(stats.total_size || 0));
                $('#processedFiles').text(stats.processed_files || 0);
                
                // Update flow chart stats
                $('#flowTotalProjects').text(stats.total_projects || 0);
                $('#flowTotalFiles').text(stats.total_files || 0);
                $('#flowProcessed').text(stats.processed_files || 0);
                
                // Update flow chart progress based on project status
                this.updateFlowChartProgress(stats);
                
            } else {
                console.warn('Stats API not available, using fallback values');
                this.updateStatsWithFallback();
            }
        } catch (error) {
            console.warn('Failed to fetch stats, using fallback values:', error.message);
            this.updateStatsWithFallback();
        }
    }
    
    updateStatsWithFallback() {
        // Use project count as fallback for total projects
        const totalProjects = this.projects.length;
        const totalFiles = this.projects.reduce((sum, project) => sum + (project.file_count || 0), 0);
        
        // Update main dashboard stats
        $('#totalProjects').text(totalProjects);
        $('#totalFiles').text(totalFiles);
        $('#totalSize').text('0 B'); // Fallback size
        $('#processedFiles').text('0'); // Fallback processed
        
        // Update flow chart stats
        $('#flowTotalProjects').text(totalProjects);
        $('#flowTotalFiles').text(totalFiles);
        $('#flowProcessed').text('0');
        
        // Update flow chart progress with fallback
        this.updateFlowChartProgress({
            total_projects: totalProjects,
            total_files: totalFiles,
            processed_files: 0
        });
    }

    updateFlowChartProgress(stats) {
        // Calculate progress based on project status
        const totalProjects = stats.total_projects || 0;
        const processedFiles = stats.processed_files || 0;
        const totalFiles = stats.total_files || 0;
        
        // Determine current step based on project status
        let currentStep = 1;
        
        if (totalProjects > 0) {
            currentStep = 2; // Projects created
        }
        
        if (totalFiles > 0) {
            currentStep = 3; // Files uploaded
        }
        
        if (processedFiles > 0) {
            currentStep = 4; // Files processed
        }
        
        if (processedFiles > 0 && totalFiles > 0 && processedFiles === totalFiles) {
            currentStep = 5; // All files processed
        }
        
        // Update flow step status
        this.updateFlowStepStatus(currentStep);
        
        // Update progress bar if it exists
        this.updateFlowProgressBar(currentStep);
    }

    updateFlowStepStatus(currentStep) {
        // Remove all status classes
        $('.flow-step').removeClass('completed active');
        
        // Add appropriate classes based on current step
        for (let i = 1; i <= 5; i++) {
            const stepElement = $(`.flow-step:nth-child(${i * 2 - 1})`);
            
            if (i < currentStep) {
                stepElement.addClass('completed');
            } else if (i === currentStep) {
                stepElement.addClass('active');
            }
        }
    }

    updateFlowProgressBar(currentStep) {
        // Calculate progress percentage
        const progressPercentage = (currentStep / 5) * 100;
        
        // Update or create progress bar
        let progressBar = $('.flow-progress-bar');
        if (progressBar.length === 0) {
            // Create progress bar if it doesn't exist
            const progressContainer = $('<div class="flow-progress"></div>');
            progressBar = $('<div class="flow-progress-bar"></div>');
            progressContainer.append(progressBar);
            $('.project-flow-chart').prepend(progressContainer);
        }
        
        // Animate progress bar
        progressBar.css('height', progressPercentage + '%');
    }

    // Add tooltips to flow steps
    addFlowStepTooltips() {
        const tooltips = {
            1: "Upload your AASX files using drag & drop or file browser",
            2: "Create projects to organize files by category or use case",
            3: "Process files to extract, transform, and load data",
            4: "Files are automatically organized by physics type",
            5: "View analytics, insights, and processed results"
        };
        
        $('.flow-step').each(function(index) {
            const stepNumber = Math.floor(index / 2) + 1;
            if (tooltips[stepNumber]) {
                $(this).attr('data-tooltip', tooltips[stepNumber]);
            }
        });
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
                    <h6 class="text-primary mb-3">Project Management Hierarchy</h6>
                    <div class="hierarchy-tree">
                        <div class="level-1">
                            <div class="node primary">📊 Project Management</div>
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

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getFileStatusInfo(status) {
        const statusInfo = {
            'pending': { color: 'warning', icon: 'clock', text: 'Pending' },
            'processing': { color: 'info', icon: 'cog', text: 'Processing' },
            'completed': { color: 'success', icon: 'check', text: 'Completed' },
            'failed': { color: 'danger', icon: 'times', text: 'Failed' },
            'skipped': { color: 'secondary', icon: 'minus', text: 'Skipped' }
        };
        return statusInfo[status] || { color: 'secondary', icon: 'question', text: 'Unknown' };
    }

    // Project Management Methods
    showCreateProjectModal() {
        $('#createProjectModal').modal('show');
    }

    resetCreateProjectForm() {
        $('#createProjectForm')[0].reset();
    }

    async createProject() {
        const formData = new FormData($('#createProjectForm')[0]);
        const projectData = {
            name: formData.get('projectName'),
            description: formData.get('projectDescription'),
            tags: formData.get('projectTags').split(',').map(tag => tag.trim()).filter(tag => tag)
        };

        try {
            const response = await fetch('/aasx/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                this.showSuccessMessage('Project created successfully!');
                $('#createProjectModal').modal('hide');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`Failed to create project: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`Error creating project: ${error.message}`);
        }
    }

    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccessMessage('Project deleted successfully!');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`Failed to delete project: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`Error deleting project: ${error.message}`);
        }
    }

    async viewProject(projectId) {
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}`);
            if (response.ok) {
                const project = await response.json();
                const filesResponse = await fetch(`/aasx/api/projects/${projectId}/files`);
                const files = filesResponse.ok ? await filesResponse.json() : [];
                this.showProjectDetails(project, files);
            } else {
                this.showErrorMessage('Failed to load project details');
            }
        } catch (error) {
            this.showErrorMessage(`Error loading project: ${error.message}`);
        }
    }

    showProjectDetails(project, files) {
        const filesHtml = files.map(file => `
            <tr>
                <td>${file.filename}</td>
                <td>${this.formatFileSize(file.file_size)}</td>
                <td>${file.uploaded_at}</td>
                <td>
                    <span class="badge bg-${this.getStatusBadgeColor(file.status)}">
                        ${file.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="projectManager.processFile('${project.project_id}', '${file.file_id}')">
                            <i class="fas fa-cog"></i> Process
                        </button>
                        <button class="btn btn-outline-danger" onclick="projectManager.deleteFile('${project.project_id}', '${file.file_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        $('#projectDetailsModal .modal-title').text(project.name);
        $('#projectDetailsModal .modal-body').html(`
            <div class="row">
                <div class="col-md-6">
                    <h6>Project Information</h6>
                    <p><strong>Description:</strong> ${project.description || 'No description'}</p>
                    <p><strong>Created:</strong> ${new Date(project.created_at).toLocaleDateString()}</p>
                    <p><strong>Files:</strong> ${project.file_count || 0}</p>
                    <p><strong>Total Size:</strong> ${this.formatFileSize(project.total_size || 0)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Files</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Filename</th>
                                    <th>Size</th>
                                    <th>Uploaded</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${filesHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `);
        $('#projectDetailsModal').modal('show');
    }

    getStatusBadgeColor(status) {
        const colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'skipped': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    // File Management Methods
    async handleFileUpload(e) {
        e.preventDefault();
        
        const useCaseSelect = $('#uploadUseCaseSelect');
        const projectSelect = $('#uploadProjectSelect');
        const fileInput = $('#aasxFileInput');
        const description = $('#fileDescription');
        
        const selectedUseCase = useCaseSelect.val();
        const projectId = projectSelect.val();
        const file = fileInput[0].files[0];
        
        if (!selectedUseCase) {
            this.showErrorMessage('Please select a use case first');
            return;
        }
        
        if (!projectId) {
            this.showErrorMessage('Please select a project');
            return;
        }
        
        if (!file) {
            this.showErrorMessage('Please select a file to upload');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', description.val() || '');
        formData.append('use_case', selectedUseCase);

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showSuccessMessage('File uploaded successfully!');
                // Reset form
                fileInput.val('');
                description.val('');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`Upload failed: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`Upload error: ${error.message}`);
        }
    }

    async handleUrlUpload(e) {
        e.preventDefault();
        
        const useCaseSelect = $('#urlUseCaseSelect');
        const projectSelect = $('#urlProjectSelect');
        const urlInput = $('#aasxFileUrl');
        const description = $('#urlFileDescription');
        
        const selectedUseCase = useCaseSelect.val();
        const projectId = projectSelect.val();
        const url = urlInput.val();
        
        if (!selectedUseCase) {
            this.showErrorMessage('Please select a use case first');
            return;
        }
        
        if (!projectId) {
            this.showErrorMessage('Please select a project');
            return;
        }
        
        if (!url) {
            this.showErrorMessage('Please enter a valid URL');
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/upload-url`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    url,
                    description: description.val() || '',
                    use_case: selectedUseCase
                })
            });

            if (response.ok) {
                this.showSuccessMessage('File uploaded from URL successfully!');
                // Reset form
                urlInput.val('');
                description.val('');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`URL upload failed: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`URL upload error: ${error.message}`);
        }
    }

    async processFile(projectId, fileId) {
        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files/${fileId}/process`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showSuccessMessage('File processing started!');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`Processing failed: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`Processing error: ${error.message}`);
        }
    }

    async deleteFile(projectId, fileId) {
        if (!confirm('Are you sure you want to delete this file?')) {
            return;
        }

        try {
            const response = await fetch(`/aasx/api/projects/${projectId}/files/${fileId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccessMessage('File deleted successfully!');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showErrorMessage(`Delete failed: ${error.detail}`);
            }
        } catch (error) {
            this.showErrorMessage(`Delete error: ${error.message}`);
        }
    }

    // Utility Methods
    showSuccessMessage(message) {
        showAlert(message, 'success');
    }

    showErrorMessage(message) {
        showAlert(message, 'danger');
    }

    uploadToProject(projectId) {
        $('#uploadProjectId').val(projectId);
        $('#uploadModal').modal('show');
    }

    // Auto-refresh functionality
    async autoRefresh() {
        await this.loadProjects();
    }

    async refreshAndSync() {
        try {
            const response = await fetch('/aasx/api/projects/sync', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccessMessage('Projects synchronized successfully!');
                await this.loadProjects();
            } else {
                this.showErrorMessage('Failed to synchronize projects');
            }
        } catch (error) {
            this.showErrorMessage(`Sync error: ${error.message}`);
        }
    }
}

// Initialize Project Manager when DOM is ready
$(document).ready(() => {
    window.projectManager = new ProjectManager();
    projectManager.init();
});