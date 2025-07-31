/**
 * Physics Modeling Use Cases JavaScript
 * Handles loading and interaction with use cases on the dedicated use cases page
 */

class PhysicsModelingUseCases {
    constructor() {
        this.useCases = {};
        this.currentCategory = 'thermal';
        this.currentUseCaseId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUseCases();
        this.loadStatistics();
    }

    setupEventListeners() {
        // Category selection
        document.querySelectorAll('.use-case-category').forEach(category => {
            category.addEventListener('click', (e) => {
                this.selectCategory(e.currentTarget.dataset.category);
            });
        });

        // Create use case button
        const createBtn = document.getElementById('createUseCaseBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.showCreateUseCaseForm();
            });
        }

        // Form submission
        const saveBtn = document.getElementById('saveUseCaseBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveUseCase();
            });
        }

        // Delete use case button
        const deleteBtn = document.getElementById('deleteUseCaseBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.deleteUseCase();
            });
        }

        // Form modal events
        const formModal = document.getElementById('useCaseFormModal');
        if (formModal) {
            formModal.addEventListener('hidden.bs.modal', () => {
                this.resetForm();
            });
        }

        // Toggle between project data and framework data
        const toggle = document.getElementById('use-project-data-toggle');
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                this.toggleDataSource(e.target.checked);
            });
        }
    }

    async loadUseCases() {
        try {
            const useProjectData = document.getElementById('use-project-data-toggle')?.checked ?? true;
            
            if (useProjectData) {
                // Load from database
                const response = await fetch('/physics-modeling/api/use-cases');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.useCases = data.use_cases || {};
                        this.displayUseCases();
                        return;
                    }
                }
            }
            
            // Fallback to framework data
            this.loadFallbackUseCases();
            
        } catch (error) {
            console.error('Error loading use cases:', error);
            this.loadFallbackUseCases();
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/physics-modeling/api/use-cases/statistics');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.statistics) {
                    this.updateStatisticsDisplay(data.statistics);
                }
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateStatisticsDisplay(stats) {
        // Update category counts
        Object.entries(stats.categories || {}).forEach(([category, count]) => {
            const categoryElement = document.querySelector(`[data-category="${category}"] small`);
            if (categoryElement) {
                categoryElement.textContent = `${count} use cases`;
            }
        });

        // Update total count
        const totalElement = document.getElementById('total-use-cases');
        if (totalElement && stats.total_use_cases !== undefined) {
            totalElement.textContent = stats.total_use_cases;
        }
    }

    selectCategory(category) {
        // Hide all sections
        document.querySelectorAll('.use-case-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const selectedSection = document.getElementById(`${category}-section`);
        if (selectedSection) {
            selectedSection.style.display = 'block';
        }

        // Update active category
        this.currentCategory = category;

        // Update category selection UI
        document.querySelectorAll('.use-case-category').forEach(cat => {
            cat.classList.remove('border-primary', 'bg-primary', 'text-white');
            cat.classList.add('border');
        });

        const activeCategory = document.querySelector(`[data-category="${category}"]`);
        if (activeCategory) {
            activeCategory.classList.remove('border');
            activeCategory.classList.add('border-primary');
        }

        // Load use cases for this category
        this.displayUseCasesForCategory(category);
    }

    displayUseCases() {
        // Display use cases for the current category
        this.displayUseCasesForCategory(this.currentCategory);
    }

    displayUseCasesForCategory(category) {
        const container = document.getElementById(`${category}-use-cases`);
        if (!container) return;

        container.innerHTML = '';

        const categoryUseCases = this.useCases[category] || [];
        
        if (categoryUseCases.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-folder-open fa-3x mb-3"></i>
                        <h5>No use cases available for this category yet.</h5>
                        <p>Create your first use case to get started.</p>
                        <button class="btn btn-primary" onclick="useCaseManager.showCreateUseCaseForm()">
                            <i class="fas fa-plus me-1"></i>Create Use Case
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        categoryUseCases.forEach(useCase => {
            const useCaseCard = this.createUseCaseCard(useCase);
            container.appendChild(useCaseCard);
        });
    }

    createUseCaseCard(useCase) {
        const col = document.createElement('div');
        col.className = 'col-lg-6 col-md-12 mb-4';
        
        const categoryIcons = {
            thermal: 'fas fa-fire text-danger',
            structural: 'fas fa-cube text-warning',
            fluid_dynamics: 'fas fa-water text-info',
            multi_physics: 'fas fa-link text-success',
            industrial: 'fas fa-industry text-secondary'
        };

        const icon = categoryIcons[useCase.category] || 'fas fa-atom text-muted';
        
        col.innerHTML = `
            <div class="card use-case-card border-0 shadow-sm h-100" data-use-case-id="${useCase.use_case_id || useCase.id}">
                <div class="card-header bg-gradient-primary text-white">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-0">
                            <i class="${icon} me-2"></i>
                            ${useCase.name}
                        </h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="useCaseManager.viewUseCaseDetails('${useCase.name}')">
                                    <i class="fas fa-eye me-1"></i>View Details
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="useCaseManager.editUseCase('${useCase.use_case_id || useCase.id}')">
                                    <i class="fas fa-edit me-1"></i>Edit
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="useCaseManager.deleteUseCase('${useCase.use_case_id || useCase.id}')">
                                    <i class="fas fa-trash me-1"></i>Delete
                                </a></li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <span class="badge bg-secondary industry-badge">
                            <i class="fas fa-industry me-1"></i>
                            ${useCase.industry || 'General'}
                        </span>
                        ${useCase.complexity ? `
                        <span class="badge bg-info ms-1">
                            <i class="fas fa-layer-group me-1"></i>${useCase.complexity}
                        </span>
                        ` : ''}
                    </div>
                    
                    <p class="text-muted small mb-3">${useCase.description || 'No description available'}</p>
                    
                    ${useCase.famous_examples && useCase.famous_examples.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="text-success">
                            <i class="fas fa-star me-1"></i>
                            Famous Examples
                        </h6>
                        <div class="small text-muted">
                            ${useCase.famous_examples.slice(0, 3).join(', ')}
                            ${useCase.famous_examples.length > 3 ? ` and ${useCase.famous_examples.length - 3} more...` : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="mt-auto">
                        <button class="btn btn-primary btn-sm" onclick="useCaseManager.viewUseCaseDetails('${useCase.name}')">
                            <i class="fas fa-info-circle me-1"></i>View Details
                        </button>
                        <button class="btn btn-success btn-sm ms-2" onclick="useCaseManager.createModelFromUseCase('${useCase.name}')">
                            <i class="fas fa-plus me-1"></i>Create Model
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }

    showCreateUseCaseForm() {
        this.currentUseCaseId = null;
        document.getElementById('useCaseFormModalTitle').innerHTML = '<i class="fas fa-plus-circle me-2"></i>Create New Use Case';
        document.getElementById('useCaseMode').value = 'create';
        document.getElementById('deleteUseCaseBtn').style.display = 'none';
        
        const modal = new bootstrap.Modal(document.getElementById('useCaseFormModal'));
        modal.show();
    }

    async editUseCase(useCaseId) {
        try {
            const response = await fetch(`/physics-modeling/api/use-cases/${useCaseId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch use case');
            }
            
            const useCase = await response.json();
            this.populateForm(useCase);
            
            this.currentUseCaseId = useCaseId;
            document.getElementById('useCaseFormModalTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Edit Use Case';
            document.getElementById('useCaseMode').value = 'edit';
            document.getElementById('deleteUseCaseBtn').style.display = 'block';
            
            const modal = new bootstrap.Modal(document.getElementById('useCaseFormModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error loading use case for editing:', error);
            this.showError('Failed to load use case for editing');
        }
    }

    populateForm(useCase) {
        document.getElementById('useCaseId').value = useCase.use_case_id || '';
        document.getElementById('useCaseName').value = useCase.name || '';
        document.getElementById('useCaseCategory').value = useCase.category || '';
        document.getElementById('useCaseIndustry').value = useCase.industry || '';
        document.getElementById('useCasePhysicsType').value = useCase.physics_type || '';
        document.getElementById('useCaseDescription').value = useCase.description || '';
        document.getElementById('useCaseComplexity').value = useCase.complexity || '';
        document.getElementById('useCaseDuration').value = useCase.expected_duration || '';
        document.getElementById('useCaseDataPoints').value = useCase.data_points || '';
        document.getElementById('useCaseTags').value = Array.isArray(useCase.tags) ? useCase.tags.join(', ') : '';
        
        // Handle array fields
        if (Array.isArray(useCase.famous_examples)) {
            document.getElementById('useCaseFamousExamples').value = useCase.famous_examples.join('\n');
        } else {
            document.getElementById('useCaseFamousExamples').value = '';
        }
        
        if (Array.isArray(useCase.optimization_targets)) {
            document.getElementById('useCaseOptimizationTargets').value = useCase.optimization_targets.join('\n');
        } else {
            document.getElementById('useCaseOptimizationTargets').value = '';
        }
        
        // Handle materials (could be JSON or string)
        if (useCase.materials) {
            if (typeof useCase.materials === 'string') {
                document.getElementById('useCaseMaterials').value = useCase.materials;
            } else {
                document.getElementById('useCaseMaterials').value = JSON.stringify(useCase.materials, null, 2);
            }
        } else {
            document.getElementById('useCaseMaterials').value = '';
        }
    }

    async saveUseCase() {
        const form = document.getElementById('useCaseForm');
        const formData = new FormData(form);
        
        const mode = formData.get('mode');
        const useCaseId = formData.get('use_case_id');
        
        try {
            const url = mode === 'edit' ? `/physics-modeling/api/use-cases/${useCaseId}` : '/physics-modeling/api/use-cases';
            const method = mode === 'edit' ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save use case');
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('useCaseFormModal'));
                modal.hide();
                
                // Reload use cases
                await this.loadUseCases();
                await this.loadStatistics();
            } else {
                throw new Error(result.error || 'Failed to save use case');
            }
            
        } catch (error) {
            console.error('Error saving use case:', error);
            this.showError(error.message);
        }
    }

    async deleteUseCase(useCaseId) {
        if (!confirm('Are you sure you want to delete this use case? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/physics-modeling/api/use-cases/${useCaseId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to delete use case');
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                
                // Close modal if open
                const modal = bootstrap.Modal.getInstance(document.getElementById('useCaseFormModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Reload use cases
                await this.loadUseCases();
                await this.loadStatistics();
            } else {
                throw new Error(result.error || 'Failed to delete use case');
            }
            
        } catch (error) {
            console.error('Error deleting use case:', error);
            this.showError(error.message);
        }
    }

    resetForm() {
        document.getElementById('useCaseForm').reset();
        document.getElementById('useCaseId').value = '';
        document.getElementById('useCaseMode').value = 'create';
        this.currentUseCaseId = null;
    }

    toggleDataSource(useProjectData) {
        const description = document.getElementById('use-case-description');
        if (useProjectData) {
            description.textContent = 'Showing use cases from your database. Create and manage custom use cases.';
        } else {
            description.textContent = 'Showing framework template use cases. Switch to database mode to create custom use cases.';
        }
        
        this.loadUseCases();
    }

    loadFallbackUseCases() {
        // Fallback use cases when database is not available
        this.useCases = {
            thermal: {
                "cpu-cooling": {
                    name: "CPU Cooling Analysis",
                    description: "Thermal management for high-performance processors",
                    industry: "Electronics",
                    category: "thermal",
                    famous_examples: ["Intel i9-13900K", "AMD Ryzen 9 7950X", "Apple M2 Pro"],
                    optimization_targets: ["Reduce temperature by 20%", "Minimize thermal resistance", "Optimize heat sink design"],
                    complexity: "advanced",
                    physics_type: "thermal"
                },
                "ev-battery": {
                    name: "EV Battery Thermal Management",
                    description: "Thermal control for electric vehicle battery packs",
                    industry: "Automotive",
                    category: "thermal",
                    famous_examples: ["Tesla Model S", "Nissan Leaf", "BMW i3"],
                    optimization_targets: ["Maintain optimal temperature range", "Prevent thermal runaway", "Maximize battery life"],
                    complexity: "expert",
                    physics_type: "thermal"
                }
            },
            structural: {
                "bridge-design": {
                    name: "Suspension Bridge Structural Analysis",
                    description: "Structural integrity analysis for large-scale bridges",
                    industry: "Civil Engineering",
                    category: "structural",
                    famous_examples: ["Golden Gate Bridge", "Brooklyn Bridge", "Akashi Kaikyō Bridge"],
                    optimization_targets: ["Minimize material usage", "Maximize load capacity", "Ensure seismic resistance"],
                    complexity: "expert",
                    physics_type: "structural"
                },
                "aircraft-wing": {
                    name: "Aircraft Wing Structural Analysis",
                    description: "Structural analysis for aircraft wing components",
                    industry: "Aerospace",
                    category: "structural",
                    famous_examples: ["Boeing 787", "Airbus A350", "F-35 Lightning II"],
                    optimization_targets: ["Reduce weight", "Maximize strength", "Minimize fatigue"],
                    complexity: "expert",
                    physics_type: "structural"
                }
            },
            fluid_dynamics: {
                "aircraft-aerodynamics": {
                    name: "Aircraft Aerodynamic Analysis",
                    description: "Aerodynamic performance optimization for aircraft",
                    industry: "Aerospace",
                    category: "fluid_dynamics",
                    famous_examples: ["Boeing 787 Dreamliner", "Airbus A380", "Concorde"],
                    optimization_targets: ["Reduce drag", "Improve lift", "Enhance fuel efficiency"],
                    complexity: "expert",
                    physics_type: "fluid_dynamics"
                },
                "automotive-aerodynamics": {
                    name: "Automotive Aerodynamic Analysis",
                    description: "Aerodynamic design for high-performance vehicles",
                    industry: "Automotive",
                    category: "fluid_dynamics",
                    famous_examples: ["Tesla Model S", "Porsche 911", "Ferrari F8"],
                    optimization_targets: ["Reduce drag coefficient", "Improve downforce", "Enhance stability"],
                    complexity: "advanced",
                    physics_type: "fluid_dynamics"
                }
            },
            multi_physics: {
                "fluid-structure": {
                    name: "Fluid-Structure Interaction Analysis",
                    description: "Coupled analysis of fluid flow and structural response",
                    industry: "General",
                    category: "multi_physics",
                    famous_examples: ["Wind turbine blades", "Submarine hulls", "Aircraft wings"],
                    optimization_targets: ["Minimize vibration", "Maximize efficiency", "Prevent fatigue"],
                    complexity: "expert",
                    physics_type: "multi_physics"
                },
                "thermal-structural": {
                    name: "Thermal-Structural Coupling Analysis",
                    description: "Coupled thermal and structural analysis",
                    industry: "General",
                    category: "multi_physics",
                    famous_examples: ["Engine components", "Electronic packaging", "Nuclear reactors"],
                    optimization_targets: ["Minimize thermal stress", "Prevent deformation", "Maximize reliability"],
                    complexity: "expert",
                    physics_type: "multi_physics"
                }
            },
            industrial: {
                "additive-manufacturing": {
                    name: "Additive Manufacturing Process Analysis",
                    description: "Process optimization for 3D printing and additive manufacturing",
                    industry: "Manufacturing",
                    category: "industrial",
                    famous_examples: ["3D Systems", "Stratasys", "EOS"],
                    optimization_targets: ["Improve print quality", "Reduce material waste", "Speed up production"],
                    complexity: "advanced",
                    physics_type: "multi_physics"
                },
                "hydrogen-economy": {
                    name: "Hydrogen Economy Infrastructure Analysis",
                    description: "Infrastructure design for hydrogen production, storage, and distribution",
                    industry: "Energy",
                    category: "industrial",
                    famous_examples: ["Siemens Energy", "Linde", "Air Liquide"],
                    optimization_targets: ["Maximize efficiency", "Minimize costs", "Ensure safety"],
                    complexity: "expert",
                    physics_type: "multi_physics"
                }
            }
        };
        
        this.displayUseCases();
    }

    showUseCaseDetails(useCaseName) {
        const useCase = this.findUseCase(useCaseName);
        if (!useCase) {
            this.showError('Use case not found');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('useCaseDetailModal'));
        
        document.getElementById('useCaseModalTitle').innerHTML = `
            <i class="fas fa-info-circle me-2"></i>${useCase.name}
        `;
        
        document.getElementById('useCaseModalBody').innerHTML = this.formatUseCaseDetails(useCase);
        
        document.getElementById('createModelFromUseCaseBtn').onclick = () => {
            this.createModelFromUseCase(useCaseName);
            modal.hide();
        };
        
        modal.show();
    }

    findUseCase(useCaseName) {
        for (const category in this.useCases) {
            for (const key in this.useCases[category]) {
                if (this.useCases[category][key].name === useCaseName) {
                    return this.useCases[category][key];
                }
            }
        }
        return null;
    }

    formatUseCaseDetails(useCase) {
        return `
            <div class="row">
                <div class="col-md-8">
                    <h6><i class="fas fa-info-circle text-primary me-1"></i>Description</h6>
                    <p>${useCase.description || 'No description available'}</p>
                    
                    <h6><i class="fas fa-industry text-warning me-1"></i>Industry</h6>
                    <p>${useCase.industry || 'General'}</p>
                    
                    <h6><i class="fas fa-layer-group text-info me-1"></i>Complexity</h6>
                    <p>${useCase.complexity || 'Not specified'}</p>
                    
                    ${useCase.famous_examples && useCase.famous_examples.length > 0 ? `
                    <h6><i class="fas fa-star text-success me-1"></i>Famous Examples</h6>
                    <ul>
                        ${useCase.famous_examples.map(example => `<li>${example}</li>`).join('')}
                    </ul>
                    ` : ''}
                    
                    ${useCase.optimization_targets && useCase.optimization_targets.length > 0 ? `
                    <h6><i class="fas fa-bullseye text-danger me-1"></i>Optimization Targets</h6>
                    <ul>
                        ${useCase.optimization_targets.map(target => `<li>${target}</li>`).join('')}
                    </ul>
                    ` : ''}
                </div>
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-header">
                            <h6 class="mb-0"><i class="fas fa-cog me-1"></i>Technical Details</h6>
                        </div>
                        <div class="card-body">
                            <p><strong>Category:</strong> ${useCase.category}</p>
                            <p><strong>Physics Type:</strong> ${useCase.physics_type || 'Multi-physics'}</p>
                            ${useCase.expected_duration ? `<p><strong>Duration:</strong> ${useCase.expected_duration}</p>` : ''}
                            ${useCase.data_points ? `<p><strong>Data Points:</strong> ${useCase.data_points}</p>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createModelFromUseCase(useCaseName) {
        // Close modal first
        const detailModal = bootstrap.Modal.getInstance(document.getElementById('useCaseDetailModal'));
        if (detailModal) {
            detailModal.hide();
        }
        
        // Manual cleanup to ensure backdrop is removed
        this.cleanupModalBackdrop();
        
        // Redirect to physics modeling page with use case pre-selected
        window.location.href = `/physics-modeling?use_case=${encodeURIComponent(useCaseName)}`;
    }

    cleanupModalBackdrop() {
        // Remove modal backdrop and restore body properties
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        document.body.classList.remove('modal-open');
        document.body.style.paddingRight = '';
    }

    showError(message) {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    showSuccess(message) {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Initialize when DOM is loaded
let useCaseManager;
document.addEventListener('DOMContentLoaded', function() {
    useCaseManager = new PhysicsModelingUseCases();
});

// Global functions for inline onclick handlers
window.createModelFromUseCase = function(useCaseName) {
    if (useCaseManager) {
        useCaseManager.createModelFromUseCase(useCaseName);
    }
};

window.viewUseCaseDetails = function(useCaseName) {
    if (useCaseManager) {
        useCaseManager.showUseCaseDetails(useCaseName);
    }
};