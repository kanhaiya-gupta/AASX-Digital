/**
 * Model Creation Operations
 * Handles API calls and business logic for physics model creation and management
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class ModelCreationOperations {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        this.availableTwins = [];
        this.availableModels = [];
    }

    /**
     * Load available digital twins from registry
     */
    async loadAvailableTwins() {
        try {
            this.utils.showProgress('Loading digital twins...');
            const response = await this.api.getAvailableTwins();
            this.availableTwins = response.twins || [];
            this.utils.hideProgress();
            return this.availableTwins;
        } catch (error) {
            this.utils.hideProgress();
            this.utils.handleError(error, 'loadAvailableTwins');
            return [];
        }
    }

    /**
     * Load available physics models
     */
    async loadAvailableModels(filters = {}) {
        try {
            this.utils.showProgress('Loading models...');
            const response = await this.api.getModels(filters);
            this.availableModels = response.models || [];
            this.utils.hideProgress();
            return this.availableModels;
        } catch (error) {
            this.utils.hideProgress();
            this.utils.handleError(error, 'loadAvailableModels');
            return [];
        }
    }

    /**
     * Create a new physics model
     */
    async createModel(modelData) {
        try {
            this.utils.showProgress('Creating physics model...');
            
            // Validate model data
            const validation = this.validateModelData(modelData);
            if (!validation.isValid) {
                this.utils.hideProgress();
                this.utils.showError(`Validation failed: ${validation.errors.join(', ')}`);
                return { success: false, errors: validation.errors };
            }

            const result = await this.api.createModel(modelData);
            this.utils.hideProgress();
            this.utils.showSuccess('Physics model created successfully!');
            
            // Refresh models list
            await this.loadAvailableModels();
            
            return { success: true, data: result };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'createModel');
        }
    }

    /**
     * Get model details
     */
    async getModel(modelId) {
        try {
            const model = await this.api.getModel(modelId);
            return { success: true, data: model };
        } catch (error) {
            return this.utils.handleError(error, 'getModel');
        }
    }

    /**
     * Update existing model
     */
    async updateModel(modelId, modelData) {
        try {
            this.utils.showProgress('Updating model...');
            
            const validation = this.validateModelData(modelData);
            if (!validation.isValid) {
                this.utils.hideProgress();
                this.utils.showError(`Validation failed: ${validation.errors.join(', ')}`);
                return { success: false, errors: validation.errors };
            }

            const result = await this.api.updateModel(modelId, modelData);
            this.utils.hideProgress();
            this.utils.showSuccess('Model updated successfully!');
            
            // Refresh models list
            await this.loadAvailableModels();
            
            return { success: true, data: result };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'updateModel');
        }
    }

    /**
     * Delete model
     */
    async deleteModel(modelId) {
        try {
            this.utils.showProgress('Deleting model...');
            await this.api.deleteModel(modelId);
            this.utils.hideProgress();
            this.utils.showSuccess('Model deleted successfully!');
            
            // Refresh models list
            await this.loadAvailableModels();
            
            return { success: true };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'deleteModel');
        }
    }

    /**
     * Validate model configuration
     */
    async validateConfiguration(configData) {
        try {
            this.utils.showProgress('Validating configuration...');
            const result = await this.api.validateModel(null, { config: configData });
            this.utils.hideProgress();
            return { success: true, data: result };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'validateConfiguration');
        }
    }

    /**
     * Load model template
     */
    async loadTemplate(templateName) {
        try {
            this.utils.showProgress('Loading template...');
            const templates = await this.api.getUseCaseTemplates();
            const template = templates.find(t => t.name === templateName);
            this.utils.hideProgress();
            
            if (template) {
                this.utils.showSuccess('Template loaded successfully!');
                return { success: true, data: template };
            } else {
                this.utils.showError('Template not found');
                return { success: false, error: 'Template not found' };
            }
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'loadTemplate');
        }
    }

    /**
     * Create model from use case
     */
    async createModelFromUseCase(useCaseName, modelData = {}) {
        try {
            this.utils.showProgress('Creating model from use case...');
            const result = await this.api.createModelFromUseCase(useCaseName, modelData);
            this.utils.hideProgress();
            this.utils.showSuccess('Model created from use case successfully!');
            
            // Refresh models list
            await this.loadAvailableModels();
            
            return { success: true, data: result };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'createModelFromUseCase');
        }
    }

    /**
     * Refresh twins list
     */
    async refreshTwins() {
        try {
            this.utils.showProgress('Refreshing twins...');
            await this.api.refreshTwins();
            const twins = await this.loadAvailableTwins();
            this.utils.hideProgress();
            this.utils.showSuccess('Twins refreshed successfully!');
            return { success: true, data: twins };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'refreshTwins');
        }
    }

    /**
     * Get twin details
     */
    async getTwinDetails(twinId) {
        try {
            const twin = await this.api.getTwinDetails(twinId);
            return { success: true, data: twin };
        } catch (error) {
            return this.utils.handleError(error, 'getTwinDetails');
        }
    }

    /**
     * Validate model data before submission
     */
    validateModelData(modelData) {
        const errors = [];
        const required = ['name', 'twin_id', 'physics_type', 'solver'];

        // Check required fields
        for (const field of required) {
            if (!modelData[field] || modelData[field].toString().trim() === '') {
                errors.push(`${field} is required`);
            }
        }

        // Validate physics type
        const validPhysicsTypes = ['thermal', 'structural', 'fluid', 'electromagnetic', 'multi_physics'];
        if (modelData.physics_type && !validPhysicsTypes.includes(modelData.physics_type)) {
            errors.push('Invalid physics type');
        }

        // Validate solver
        const validSolvers = ['fenics', 'openfoam', 'sfepy', 'custom'];
        if (modelData.solver && !validSolvers.includes(modelData.solver)) {
            errors.push('Invalid solver');
        }

        // Validate material properties
        if (modelData.material_properties) {
            const materialProps = modelData.material_properties;
            if (materialProps.density && materialProps.density <= 0) {
                errors.push('Density must be positive');
            }
            if (materialProps.youngs_modulus && materialProps.youngs_modulus <= 0) {
                errors.push("Young's modulus must be positive");
            }
            if (materialProps.poissons_ratio && (materialProps.poissons_ratio < 0 || materialProps.poissons_ratio > 0.5)) {
                errors.push("Poisson's ratio must be between 0 and 0.5");
            }
        }

        // Validate boundary conditions
        if (modelData.boundary_conditions) {
            const bc = modelData.boundary_conditions;
            if (bc.temperature && bc.temperature < -273.15) {
                errors.push('Temperature cannot be below absolute zero');
            }
            if (bc.pressure && bc.pressure < 0) {
                errors.push('Pressure must be non-negative');
            }
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Get physics type options based on twin capabilities
     */
    getPhysicsTypeOptions(twinId) {
        const twin = this.availableTwins.find(t => t.twin_id === twinId);
        if (!twin) return [];

        const allPhysicsTypes = [
            { value: 'thermal', label: 'Thermal Analysis', icon: 'fas fa-fire' },
            { value: 'structural', label: 'Structural Analysis', icon: 'fas fa-cog' },
            { value: 'fluid', label: 'Fluid Dynamics', icon: 'fas fa-wind' },
            { value: 'electromagnetic', label: 'Electromagnetic', icon: 'fas fa-bolt' },
            { value: 'multi_physics', label: 'Multi-Physics', icon: 'fas fa-layer-group' }
        ];

        // Filter based on twin capabilities
        if (twin.capabilities && twin.capabilities.physics_types) {
            return allPhysicsTypes.filter(pt => 
                twin.capabilities.physics_types.includes(pt.value)
            );
        }

        return allPhysicsTypes;
    }

    /**
     * Get solver options based on physics type
     */
    getSolverOptions(physicsType) {
        const solverMap = {
            'thermal': [
                { value: 'fenics', label: 'FEniCS (FEA)', description: 'Finite element analysis' },
                { value: 'sfepy', label: 'SfePy (FEA)', description: 'Simple finite elements in Python' }
            ],
            'structural': [
                { value: 'fenics', label: 'FEniCS (FEA)', description: 'Finite element analysis' },
                { value: 'sfepy', label: 'SfePy (FEA)', description: 'Simple finite elements in Python' }
            ],
            'fluid': [
                { value: 'openfoam', label: 'OpenFOAM (CFD)', description: 'Computational fluid dynamics' },
                { value: 'fenics', label: 'FEniCS (FEA)', description: 'Finite element analysis' }
            ],
            'electromagnetic': [
                { value: 'fenics', label: 'FEniCS (FEA)', description: 'Finite element analysis' },
                { value: 'custom', label: 'Custom Solver', description: 'Custom electromagnetic solver' }
            ],
            'multi_physics': [
                { value: 'fenics', label: 'FEniCS (FEA)', description: 'Finite element analysis' },
                { value: 'openfoam', label: 'OpenFOAM (CFD)', description: 'Computational fluid dynamics' },
                { value: 'custom', label: 'Custom Solver', description: 'Custom multi-physics solver' }
            ]
        };

        return solverMap[physicsType] || [];
    }

    /**
     * Get material library options
     */
    getMaterialLibrary() {
        return [
            { value: 'steel', label: 'Steel (Structural)', properties: { density: 7850, youngs_modulus: 200, poissons_ratio: 0.3 } },
            { value: 'aluminum', label: 'Aluminum (Lightweight)', properties: { density: 2700, youngs_modulus: 70, poissons_ratio: 0.35 } },
            { value: 'copper', label: 'Copper (Thermal)', properties: { density: 8960, thermal_conductivity: 400, specific_heat: 385 } },
            { value: 'composite', label: 'Composite (Advanced)', properties: { density: 1600, youngs_modulus: 45, poissons_ratio: 0.25 } },
            { value: 'ceramic', label: 'Ceramic (High-Temp)', properties: { density: 3900, thermal_conductivity: 30, specific_heat: 800 } },
            { value: 'polymer', label: 'Polymer (Flexible)', properties: { density: 1200, youngs_modulus: 3, poissons_ratio: 0.4 } }
        ];
    }

    /**
     * Get boundary condition templates
     */
    getBoundaryConditionTemplates() {
        return [
            { value: 'thermal_radiation', label: 'Thermal Radiation', type: 'thermal' },
            { value: 'thermal_convection', label: 'Thermal Convection', type: 'thermal' },
            { value: 'structural_fixed', label: 'Structural Fixed Support', type: 'structural' },
            { value: 'structural_pressure', label: 'Structural Pressure Load', type: 'structural' },
            { value: 'fluid_inlet', label: 'Fluid Inlet', type: 'fluid' },
            { value: 'fluid_outlet', label: 'Fluid Outlet', type: 'fluid' },
            { value: 'fluid_wall', label: 'Fluid Wall', type: 'fluid' },
            { value: 'electromagnetic_current', label: 'Electromagnetic Current', type: 'electromagnetic' },
            { value: 'multi_physics_coupling', label: 'Multi-Physics Coupling', type: 'multi_physics' }
        ];
    }
}

// Export the operations class
export default ModelCreationOperations; 