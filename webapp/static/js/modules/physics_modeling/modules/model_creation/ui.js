/**
 * Model Creation UI
 * Handles user interface interactions and DOM manipulation for model creation
 */

import ModelCreationOperations from './operations.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class ModelCreationUI {
    constructor() {
        this.operations = new ModelCreationOperations();
        this.utils = new PhysicsModelingUtils();
        this.currentTwin = null;
        this.currentPhysicsType = null;
        this.formData = {};
        
        this.init();
    }

    async init() {
        console.log('Initializing Model Creation UI...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadInitialData();
        
        // Setup form validation
        this.setupFormValidation();
        
        console.log('Model Creation UI initialized successfully');
    }

    /**
     * Setup event listeners for form interactions
     */
    setupEventListeners() {
        // Model creation form submission
        const form = document.getElementById('model-creation-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission();
            });
        }

        // Twin selection change
        const twinSelect = document.getElementById('twin-select');
        if (twinSelect) {
            twinSelect.addEventListener('change', (e) => {
                this.onTwinSelectionChange(e.target.value);
            });
        }

        // Refresh twins button
        const refreshTwinsBtn = document.getElementById('refresh-twins-btn');
        if (refreshTwinsBtn) {
            refreshTwinsBtn.addEventListener('click', () => {
                this.refreshTwins();
            });
        }

        // Physics type selection change
        const physicsTypeSelect = document.getElementById('physics-type-select');
        if (physicsTypeSelect) {
            physicsTypeSelect.addEventListener('change', (e) => {
                this.onPhysicsTypeChange(e.target.value);
            });
        }

        // Material library selection
        const materialLibrarySelect = document.getElementById('material-library-select');
        if (materialLibrarySelect) {
            materialLibrarySelect.addEventListener('change', (e) => {
                this.onMaterialLibraryChange(e.target.value);
            });
        }

        // Boundary condition template selection
        const bcTemplateSelect = document.getElementById('bc-template-select');
        if (bcTemplateSelect) {
            bcTemplateSelect.addEventListener('change', (e) => {
                this.onBoundaryConditionTemplateChange(e.target.value);
            });
        }

        // Template loading button
        const loadTemplateBtn = document.getElementById('load-template-btn');
        if (loadTemplateBtn) {
            loadTemplateBtn.addEventListener('click', () => {
                this.loadTemplate();
            });
        }

        // Configuration validation button
        const validateConfigBtn = document.getElementById('validate-config-btn');
        if (validateConfigBtn) {
            validateConfigBtn.addEventListener('click', () => {
                this.validateConfiguration();
            });
        }

        // Preview model button
        const previewModelBtn = document.getElementById('preview-model-btn');
        if (previewModelBtn) {
            previewModelBtn.addEventListener('click', () => {
                this.previewModel();
            });
        }

        // Advanced properties toggle
        const toggleAdvancedPropsBtn = document.getElementById('toggle-advanced-properties');
        if (toggleAdvancedPropsBtn) {
            toggleAdvancedPropsBtn.addEventListener('click', () => {
                this.toggleAdvancedProperties();
            });
        }

        // Add boundary condition button
        const addBcBtn = document.getElementById('add-boundary-condition');
        if (addBcBtn) {
            addBcBtn.addEventListener('click', () => {
                this.addBoundaryCondition();
            });
        }
    }

    /**
     * Load initial data for the form
     */
    async loadInitialData() {
        try {
            // Load available twins
            await this.operations.loadAvailableTwins();
            this.populateTwinSelect();

            // Load available models for reference
            await this.operations.loadAvailableModels();

            // Setup material library
            this.setupMaterialLibrary();

            // Setup boundary condition templates
            this.setupBoundaryConditionTemplates();

        } catch (error) {
            this.utils.handleError(error, 'loadInitialData');
        }
    }

    /**
     * Populate twin selection dropdown
     */
    populateTwinSelect() {
        const twinSelect = document.getElementById('twin-select');
        if (!twinSelect) return;

        // Clear existing options
        twinSelect.innerHTML = '<option value="">Select a digital twin...</option>';

        // Add twin options
        this.operations.availableTwins.forEach(twin => {
            const option = document.createElement('option');
            option.value = twin.twin_id; // Use twin_id instead of id
            option.textContent = `${twin.name} (${twin.status})`; // Use status instead of type
            option.setAttribute('data-twin', JSON.stringify(twin));
            twinSelect.appendChild(option);
        });
    }

    /**
     * Handle twin selection change
     */
    async onTwinSelectionChange(twinId) {
        if (!twinId) {
            this.currentTwin = null;
            this.clearPhysicsTypeOptions();
            return;
        }

        try {
            // Get twin details
            const result = await this.operations.getTwinDetails(twinId);
            if (result.success) {
                this.currentTwin = result.data;
                
                // Update physics type options based on twin capabilities
                this.updatePhysicsTypeOptions();
                
                // Update form with twin information
                this.updateFormWithTwinInfo();
                
                this.utils.showInfo(`Selected twin: ${this.currentTwin.name}`);
            }
        } catch (error) {
            this.utils.handleError(error, 'onTwinSelectionChange');
        }
    }

    /**
     * Update physics type options based on selected twin
     */
    updatePhysicsTypeOptions() {
        const physicsTypeSelect = document.getElementById('physics-type-select');
        if (!physicsTypeSelect || !this.currentTwin) return;

        // Clear existing options
        physicsTypeSelect.innerHTML = '<option value="">Select physics type...</option>';

        // Get physics type options for this twin
        const options = this.operations.getPhysicsTypeOptions(this.currentTwin.id);
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.innerHTML = `<i class="${option.icon}"></i> ${option.label}`;
            physicsTypeSelect.appendChild(optionElement);
        });
    }

    /**
     * Clear physics type options
     */
    clearPhysicsTypeOptions() {
        const physicsTypeSelect = document.getElementById('physics-type-select');
        if (physicsTypeSelect) {
            physicsTypeSelect.innerHTML = '<option value="">Select physics type...</option>';
        }
    }

    /**
     * Update form with twin information
     */
    updateFormWithTwinInfo() {
        if (!this.currentTwin) return;

        // Update any twin-specific form fields
        const twinInfoElement = document.getElementById('twin-info');
        if (twinInfoElement) {
            twinInfoElement.innerHTML = `
                <div class="alert alert-info">
                    <strong>Selected Twin:</strong> ${this.currentTwin.name}<br>
                    <strong>Type:</strong> ${this.currentTwin.type}<br>
                    <strong>Description:</strong> ${this.currentTwin.description || 'No description available'}
                </div>
            `;
        }
    }

    /**
     * Handle physics type change
     */
    onPhysicsTypeChange(physicsType) {
        if (!physicsType) {
            this.currentPhysicsType = null;
            this.clearSolverOptions();
            return;
        }

        this.currentPhysicsType = physicsType;
        
        // Update solver options based on physics type
        this.updateSolverOptions();
        
        // Update boundary condition options
        this.updateBoundaryConditionOptions();
        
        // Update form validation rules
        this.updateFormValidation();
        
        this.utils.showInfo(`Selected physics type: ${physicsType}`);
    }

    /**
     * Update solver options based on physics type
     */
    updateSolverOptions() {
        const solverSelect = document.getElementById('solver-select');
        if (!solverSelect || !this.currentPhysicsType) return;

        // Clear existing options
        solverSelect.innerHTML = '<option value="">Select solver...</option>';

        // Get solver options for this physics type
        const options = this.operations.getSolverOptions(this.currentPhysicsType);
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            optionElement.title = option.description;
            solverSelect.appendChild(optionElement);
        });
    }

    /**
     * Clear solver options
     */
    clearSolverOptions() {
        const solverSelect = document.getElementById('solver-select');
        if (solverSelect) {
            solverSelect.innerHTML = '<option value="">Select solver...</option>';
        }
    }

    /**
     * Update boundary condition options
     */
    updateBoundaryConditionOptions() {
        const bcTemplateSelect = document.getElementById('bc-template-select');
        if (!bcTemplateSelect || !this.currentPhysicsType) return;

        // Clear existing options
        bcTemplateSelect.innerHTML = '<option value="">Select template...</option>';

        // Get boundary condition templates for this physics type
        const templates = this.operations.getBoundaryConditionTemplates();
        const filteredTemplates = templates.filter(t => t.type === this.currentPhysicsType);
        
        filteredTemplates.forEach(template => {
            const optionElement = document.createElement('option');
            optionElement.value = template.value;
            optionElement.textContent = template.label;
            bcTemplateSelect.appendChild(optionElement);
        });
    }

    /**
     * Setup material library
     */
    setupMaterialLibrary() {
        const materialLibrarySelect = document.getElementById('material-library-select');
        if (!materialLibrarySelect) return;

        // Clear existing options
        materialLibrarySelect.innerHTML = '<option value="">Select from library...</option>';

        // Get material library
        const materials = this.operations.getMaterialLibrary();
        
        materials.forEach(material => {
            const optionElement = document.createElement('option');
            optionElement.value = material.value;
            optionElement.textContent = material.label;
            optionElement.setAttribute('data-properties', JSON.stringify(material.properties));
            materialLibrarySelect.appendChild(optionElement);
        });
    }

    /**
     * Handle material library selection change
     */
    onMaterialLibraryChange(materialType) {
        if (!materialType) return;

        const materialLibrarySelect = document.getElementById('material-library-select');
        const selectedOption = materialLibrarySelect.querySelector(`option[value="${materialType}"]`);
        
        if (selectedOption) {
            const properties = JSON.parse(selectedOption.getAttribute('data-properties'));
            this.populateMaterialProperties(properties);
            this.utils.showInfo(`Loaded material properties for ${materialType}`);
        }
    }

    /**
     * Populate material properties form fields
     */
    populateMaterialProperties(properties) {
        Object.entries(properties).forEach(([key, value]) => {
            const input = document.getElementById(key.replace(/_/g, '-'));
            if (input) {
                input.value = value;
            }
        });
    }

    /**
     * Setup boundary condition templates
     */
    setupBoundaryConditionTemplates() {
        const bcTemplateSelect = document.getElementById('bc-template-select');
        if (!bcTemplateSelect) return;

        // Clear existing options
        bcTemplateSelect.innerHTML = '<option value="">Select template...</option>';

        // Get all boundary condition templates
        const templates = this.operations.getBoundaryConditionTemplates();
        
        templates.forEach(template => {
            const optionElement = document.createElement('option');
            optionElement.value = template.value;
            optionElement.textContent = template.label;
            bcTemplateSelect.appendChild(optionElement);
        });
    }

    /**
     * Handle boundary condition template change
     */
    onBoundaryConditionTemplateChange(templateType) {
        if (!templateType) return;

        // Load template-specific boundary conditions
        this.loadBoundaryConditionTemplate(templateType);
        this.utils.showInfo(`Loaded boundary condition template: ${templateType}`);
    }

    /**
     * Load boundary condition template
     */
    loadBoundaryConditionTemplate(templateType) {
        const templateValues = {
            'thermal_radiation': { temperature: 300, heat_flux: 500 },
            'thermal_convection': { temperature: 25, convection_coeff: 10 },
            'structural_fixed': { displacement: 0, force: 0 },
            'structural_pressure': { pressure: 101325, force: 1000 },
            'fluid_inlet': { velocity: 1, pressure: 101325 },
            'fluid_outlet': { pressure: 101325, velocity: 0 },
            'fluid_wall': { velocity: 0, pressure: 101325 }
        };

        const values = templateValues[templateType] || {};
        Object.entries(values).forEach(([key, value]) => {
            const input = document.getElementById(`bc-${key.replace(/_/g, '-')}`);
            if (input) {
                input.value = value;
            }
        });
    }

    /**
     * Handle form submission
     */
    async handleFormSubmission() {
        try {
            // Get form data
            const formData = this.getFormData();
            
            // Validate form data
            const validation = this.validateFormData(formData);
            if (!validation.isValid) {
                this.utils.showError(`Validation failed: ${validation.errors.join(', ')}`);
                return;
            }

            // Create model
            const result = await this.operations.createModel(formData);
            if (result.success) {
                this.resetForm();
                this.utils.showSuccess('Physics model created successfully!');
                
                // Trigger model list refresh
                this.triggerModelListRefresh();
            }
        } catch (error) {
            this.utils.handleError(error, 'handleFormSubmission');
        }
    }

    /**
     * Get form data
     */
    getFormData() {
        const form = document.getElementById('model-creation-form');
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        // Basic configuration
        data.name = formData.get('name') || `Model_${Date.now()}`;
        data.twin_id = formData.get('twin-select');
        data.physics_type = formData.get('physics-type-select');
        data.solver = formData.get('solver-select');
        data.ai_integration = formData.get('ai-insights-toggle') === 'on';
        data.complexity = formData.get('model-complexity') || 'basic';

        // Material properties
        data.material_properties = {
            density: parseFloat(formData.get('density')) || 7850,
            youngs_modulus: parseFloat(formData.get('youngs-modulus')) || 200,
            poissons_ratio: parseFloat(formData.get('poissons-ratio')) || 0.3,
            thermal_conductivity: parseFloat(formData.get('thermal-conductivity')) || 50,
            specific_heat: parseFloat(formData.get('specific-heat')) || 460,
            thermal_expansion: parseFloat(formData.get('thermal-expansion')) || 12e-6
        };

        // Boundary conditions
        data.boundary_conditions = {
            temperature: parseFloat(formData.get('bc-temperature')) || 25,
            heat_flux: parseFloat(formData.get('bc-heat-flux')) || 1000,
            convection_coeff: parseFloat(formData.get('bc-convection-coeff')) || 10,
            displacement: parseFloat(formData.get('bc-displacement')) || 0,
            force: parseFloat(formData.get('bc-force')) || 1000,
            pressure: parseFloat(formData.get('bc-pressure')) || 101325,
            velocity: parseFloat(formData.get('bc-velocity')) || 1,
            turbulence: parseFloat(formData.get('bc-turbulence')) || 5,
            viscosity: parseFloat(formData.get('bc-viscosity')) || 1e-3
        };

        // Geometry and mesh
        data.geometry = {
            type: formData.get('geometry-type') || '3d',
            mesh_quality: formData.get('mesh-quality') || 'medium',
            element_type: formData.get('element-type') || 'tetrahedral'
        };

        return data;
    }

    /**
     * Validate form data
     */
    validateFormData(formData) {
        return this.operations.validateModelData(formData);
    }

    /**
     * Reset form
     */
    resetForm() {
        const form = document.getElementById('model-creation-form');
        if (form) {
            form.reset();
        }
        
        // Clear dynamic content
        this.clearPhysicsTypeOptions();
        this.clearSolverOptions();
        
        // Reset current state
        this.currentTwin = null;
        this.currentPhysicsType = null;
        this.formData = {};
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const validationRules = {
            'twin-select': { required: true },
            'physics-type-select': { required: true },
            'solver-select': { required: true },
            'density': { required: true, min: 0 },
            'youngs-modulus': { required: true, min: 0 },
            'poissons-ratio': { required: true, min: 0, max: 0.5 }
        };

        // Add real-time validation
        Object.keys(validationRules).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => {
                    this.validateField(fieldId, validationRules[fieldId]);
                });
            }
        });
    }

    /**
     * Validate individual field
     */
    validateField(fieldId, rules) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        const value = field.value;
        const errors = [];

        if (rules.required && (!value || value.trim() === '')) {
            errors.push('This field is required');
        }

        if (rules.min && value && parseFloat(value) < rules.min) {
            errors.push(`Value must be at least ${rules.min}`);
        }

        if (rules.max && value && parseFloat(value) > rules.max) {
            errors.push(`Value must be no more than ${rules.max}`);
        }

        // Update field styling
        if (errors.length > 0) {
            field.classList.add('is-invalid');
            this.showFieldError(fieldId, errors[0]);
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            this.hideFieldError(fieldId);
        }
    }

    /**
     * Show field error message
     */
    showFieldError(fieldId, message) {
        let errorDiv = document.getElementById(`${fieldId}-error`);
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = `${fieldId}-error`;
            errorDiv.className = 'invalid-feedback';
            const field = document.getElementById(fieldId);
            if (field && field.parentNode) {
                field.parentNode.appendChild(errorDiv);
            }
        }
        errorDiv.textContent = message;
    }

    /**
     * Hide field error message
     */
    hideFieldError(fieldId) {
        const errorDiv = document.getElementById(`${fieldId}-error`);
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Update form validation based on current state
     */
    updateFormValidation() {
        // Update validation rules based on current physics type
        if (this.currentPhysicsType) {
            // Add physics-specific validation rules
            console.log(`Updated validation for physics type: ${this.currentPhysicsType}`);
        }
    }

    /**
     * Load template
     */
    async loadTemplate() {
        // Show template selection modal or dropdown
        this.utils.showInfo('Template loading functionality - to be implemented');
    }

    /**
     * Validate configuration
     */
    async validateConfiguration() {
        try {
            const formData = this.getFormData();
            const result = await this.operations.validateConfiguration(formData);
            
            if (result.success) {
                this.utils.showSuccess('Configuration is valid!');
                this.displayValidationResults(result.data);
            } else {
                this.utils.showError('Configuration validation failed');
            }
        } catch (error) {
            this.utils.handleError(error, 'validateConfiguration');
        }
    }

    /**
     * Display validation results
     */
    displayValidationResults(results) {
        // Create and show validation results modal
        const modal = this.createValidationResultsModal(results);
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Remove modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    /**
     * Create validation results modal
     */
    createValidationResultsModal(results) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Configuration Validation Results</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-success">
                            <strong>Validation Status:</strong> ${results.status}<br>
                            <strong>Score:</strong> ${results.score || 'N/A'}<br>
                            <strong>Issues Found:</strong> ${results.issues?.length || 0}
                        </div>
                        ${results.issues ? `
                            <h6>Issues:</h6>
                            <ul>
                                ${results.issues.map(issue => `<li>${issue}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Preview model
     */
    previewModel() {
        const formData = this.getFormData();
        this.utils.showInfo('Model preview functionality - to be implemented');
        console.log('Model preview data:', formData);
    }

    /**
     * Toggle advanced properties
     */
    toggleAdvancedProperties() {
        const advancedSection = document.getElementById('advanced-properties-section');
        if (advancedSection) {
            const isVisible = advancedSection.style.display !== 'none';
            advancedSection.style.display = isVisible ? 'none' : 'block';
            
            const toggleBtn = document.getElementById('toggle-advanced-properties');
            if (toggleBtn) {
                toggleBtn.innerHTML = isVisible ? 
                    '<i class="fas fa-plus me-1"></i>Show Advanced Properties' :
                    '<i class="fas fa-minus me-1"></i>Hide Advanced Properties';
            }
        }
    }

    /**
     * Add boundary condition
     */
    addBoundaryCondition() {
        this.utils.showInfo('Add boundary condition functionality - to be implemented');
    }

    /**
     * Refresh twins
     */
    async refreshTwins() {
        try {
            const result = await this.operations.refreshTwins();
            if (result.success) {
                this.populateTwinSelect();
            }
        } catch (error) {
            this.utils.handleError(error, 'refreshTwins');
        }
    }

    /**
     * Trigger model list refresh
     */
    triggerModelListRefresh() {
        // Dispatch custom event to notify other modules
        const event = new CustomEvent('modelListRefresh', {
            detail: { timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }
}

// Export the UI class
export default ModelCreationUI; 