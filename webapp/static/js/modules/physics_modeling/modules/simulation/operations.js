/**
 * Simulation Operations
 * Handles API calls and business logic for physics simulation management
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class SimulationOperations {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        this.activeSimulations = new Map();
        this.simulationStatus = new Map();
        this.monitoringIntervals = new Map();
    }

    /**
     * Run a new simulation using a plugin
     */
    async runSimulation(simulationData) {
        try {
            this.utils.showProgress('Starting simulation...');
            
            // Validate simulation data
            const validation = this.validateSimulationData(simulationData);
            if (!validation.isValid) {
                this.utils.hideProgress();
                this.utils.showError(`Validation failed: ${validation.errors.join(', ')}`);
                return { success: false, errors: validation.errors };
            }

            // Use the new plugin-based simulation endpoint
            const result = await this.api.runSimulationWithPlugin(simulationData);
            this.utils.hideProgress();
            
            if (result.success) {
                const simulationId = result.data.simulation_id;
                this.activeSimulations.set(simulationId, result.data);
                this.simulationStatus.set(simulationId, 'running');
                
                // Start monitoring the simulation
                this.startSimulationMonitoring(simulationId);
                
                this.utils.showSuccess('Simulation started successfully!');
                return { success: true, data: result.data };
            } else {
                this.utils.showError('Failed to start simulation');
                return { success: false, error: result.error };
            }
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'runSimulation');
        }
    }

    /**
     * Get simulation status
     */
    async getSimulationStatus(simulationId) {
        try {
            const result = await this.api.getSimulationStatus(simulationId);
            if (result.success) {
                this.simulationStatus.set(simulationId, result.data.status);
                return { success: true, data: result.data };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return this.utils.handleError(error, 'getSimulationStatus');
        }
    }

    /**
     * Cancel simulation
     */
    async cancelSimulation(simulationId) {
        try {
            this.utils.showProgress('Cancelling simulation...');
            const result = await this.api.cancelSimulation(simulationId);
            this.utils.hideProgress();
            
            if (result.success) {
                this.simulationStatus.set(simulationId, 'cancelled');
                this.stopSimulationMonitoring(simulationId);
                this.activeSimulations.delete(simulationId);
                
                this.utils.showSuccess('Simulation cancelled successfully!');
                return { success: true };
            } else {
                this.utils.showError('Failed to cancel simulation');
                return { success: false, error: result.error };
            }
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'cancelSimulation');
        }
    }

    /**
     * Get simulation results
     */
    async getSimulationResults(simulationId) {
        try {
            this.utils.showProgress('Loading simulation results...');
            const result = await this.api.getSimulationResults(simulationId);
            this.utils.hideProgress();
            
            if (result.success) {
                return { success: true, data: result.data };
            } else {
                this.utils.showError('Failed to load simulation results');
                return { success: false, error: result.error };
            }
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'getSimulationResults');
        }
    }

    /**
     * List simulations with filters
     */
    async listSimulations(filters = {}) {
        try {
            this.utils.showProgress('Loading simulations...');
            const response = await this.api.listSimulations(filters);
            this.utils.hideProgress();
            
            return { success: true, data: response.simulations || [] };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'listSimulations');
        }
    }

    /**
     * Get active simulations count
     */
    async getActiveSimulationsCount() {
        try {
            const response = await this.api.getActiveSimulationsCount();
            return { success: true, data: response.active_count || 0 };
        } catch (error) {
            return this.utils.handleError(error, 'getActiveSimulationsCount');
        }
    }

    /**
     * Start monitoring a simulation
     */
    startSimulationMonitoring(simulationId) {
        // Stop any existing monitoring for this simulation
        this.stopSimulationMonitoring(simulationId);
        
        // Start periodic status checks
        const interval = setInterval(async () => {
            try {
                const statusResult = await this.getSimulationStatus(simulationId);
                if (statusResult.success) {
                    const status = statusResult.data;
                    this.simulationStatus.set(simulationId, status.status);
                    
                    // Update UI with new status
                    this.updateSimulationStatusUI(simulationId, status);
                    
                    // Check if simulation is complete
                    if (['completed', 'failed', 'cancelled'].includes(status.status)) {
                        this.stopSimulationMonitoring(simulationId);
                        this.activeSimulations.delete(simulationId);
                        
                        if (status.status === 'completed') {
                            this.utils.showSuccess(`Simulation ${simulationId} completed successfully!`);
                        } else if (status.status === 'failed') {
                            this.utils.showError(`Simulation ${simulationId} failed`);
                        } else if (status.status === 'cancelled') {
                            this.utils.showInfo(`Simulation ${simulationId} was cancelled`);
                        }
                    }
                }
            } catch (error) {
                console.error(`Error monitoring simulation ${simulationId}:`, error);
            }
        }, 2000); // Check every 2 seconds
        
        this.monitoringIntervals.set(simulationId, interval);
    }

    /**
     * Stop monitoring a simulation
     */
    stopSimulationMonitoring(simulationId) {
        const interval = this.monitoringIntervals.get(simulationId);
        if (interval) {
            clearInterval(interval);
            this.monitoringIntervals.delete(simulationId);
        }
    }

    /**
     * Update simulation status in UI
     */
    updateSimulationStatusUI(simulationId, status) {
        // Dispatch custom event for UI updates
        const event = new CustomEvent('simulationStatusUpdate', {
            detail: {
                simulationId: simulationId,
                status: status,
                timestamp: Date.now()
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Validate simulation data for plugin-based simulations
     */
    validateSimulationData(simulationData) {
        const errors = [];
        
        // Check required fields for plugin-based simulation
        if (!simulationData.twin_id) {
            errors.push('twin_id is required');
        }
        
        if (!simulationData.plugin_id) {
            errors.push('plugin_id is required');
        }
        
        // Validate parameters if provided
        if (simulationData.parameters && typeof simulationData.parameters !== 'object') {
            errors.push('parameters must be an object');
        }
        
        // Additional validation can be added here based on plugin requirements
        // This would typically involve checking against the plugin's parameter definitions
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Get simulation type options
     */
    getSimulationTypeOptions() {
        return [
            { value: 'steady_state', label: 'Steady State', description: 'Solve for equilibrium conditions' },
            { value: 'transient', label: 'Transient', description: 'Time-dependent analysis' },
            { value: 'optimization', label: 'Optimization', description: 'Parameter optimization' },
            { value: 'parametric', label: 'Parametric Study', description: 'Parameter sweep analysis' },
            { value: 'sensitivity', label: 'Sensitivity Analysis', description: 'Parameter sensitivity study' }
        ];
    }

    /**
     * Get solver options for simulation
     */
    getSolverOptions(physicsType) {
        const solverMap = {
            'thermal': [
                { value: 'fenics_thermal', label: 'FEniCS Thermal', description: 'Finite element thermal solver' },
                { value: 'sfepy_thermal', label: 'SfePy Thermal', description: 'Simple finite elements thermal solver' }
            ],
            'structural': [
                { value: 'fenics_structural', label: 'FEniCS Structural', description: 'Finite element structural solver' },
                { value: 'sfepy_structural', label: 'SfePy Structural', description: 'Simple finite elements structural solver' }
            ],
            'fluid': [
                { value: 'openfoam_fluid', label: 'OpenFOAM Fluid', description: 'Computational fluid dynamics solver' },
                { value: 'fenics_fluid', label: 'FEniCS Fluid', description: 'Finite element fluid solver' }
            ],
            'electromagnetic': [
                { value: 'fenics_electromagnetic', label: 'FEniCS Electromagnetic', description: 'Finite element electromagnetic solver' },
                { value: 'custom_electromagnetic', label: 'Custom Electromagnetic', description: 'Custom electromagnetic solver' }
            ],
            'multi_physics': [
                { value: 'fenics_multiphysics', label: 'FEniCS Multi-Physics', description: 'Finite element multi-physics solver' },
                { value: 'openfoam_multiphysics', label: 'OpenFOAM Multi-Physics', description: 'CFD multi-physics solver' },
                { value: 'custom_multiphysics', label: 'Custom Multi-Physics', description: 'Custom multi-physics solver' }
            ]
        };

        return solverMap[physicsType] || [];
    }

    /**
     * Get default simulation parameters
     */
    getDefaultSimulationParameters(simulationType) {
        const defaults = {
            'steady_state': {
                convergence_tolerance: 1e-6,
                max_iterations: 1000,
                output_frequency: 1
            },
            'transient': {
                time_range: 100,
                time_step: 0.1,
                convergence_tolerance: 1e-6,
                max_iterations: 1000,
                output_frequency: 10
            },
            'optimization': {
                convergence_tolerance: 1e-6,
                max_iterations: 500,
                output_frequency: 1,
                optimization_method: 'gradient_descent'
            },
            'parametric': {
                convergence_tolerance: 1e-6,
                max_iterations: 1000,
                output_frequency: 1,
                parameter_steps: 10
            },
            'sensitivity': {
                convergence_tolerance: 1e-6,
                max_iterations: 1000,
                output_frequency: 1,
                sensitivity_method: 'finite_difference'
            }
        };

        return defaults[simulationType] || {};
    }

    /**
     * Calculate estimated simulation time
     */
    calculateEstimatedTime(simulationData) {
        const baseTime = 60; // Base time in seconds
        let multiplier = 1;

        // Adjust based on simulation type
        switch (simulationData.simulation_type) {
            case 'steady_state':
                multiplier = 1;
                break;
            case 'transient':
                multiplier = Math.max(1, simulationData.time_range / 100);
                break;
            case 'optimization':
                multiplier = 5;
                break;
            case 'parametric':
                multiplier = simulationData.parameter_steps || 10;
                break;
            case 'sensitivity':
                multiplier = 3;
                break;
        }

        // Adjust based on mesh quality
        const meshQualityMultiplier = {
            'coarse': 0.5,
            'medium': 1,
            'fine': 2,
            'very_fine': 4
        };
        multiplier *= meshQualityMultiplier[simulationData.mesh_quality] || 1;

        // Adjust based on physics complexity
        const complexityMultiplier = {
            'basic': 1,
            'advanced': 2,
            'expert': 4
        };
        multiplier *= complexityMultiplier[simulationData.complexity] || 1;

        return Math.round(baseTime * multiplier);
    }

    /**
     * Get simulation status summary
     */
    getSimulationStatusSummary() {
        const summary = {
            total: this.simulationStatus.size,
            running: 0,
            completed: 0,
            failed: 0,
            cancelled: 0,
            pending: 0
        };

        for (const status of this.simulationStatus.values()) {
            if (summary.hasOwnProperty(status)) {
                summary[status]++;
            }
        }

        return summary;
    }

    /**
     * Cleanup completed simulations
     */
    cleanupCompletedSimulations() {
        const completedStatuses = ['completed', 'failed', 'cancelled'];
        
        for (const [simulationId, status] of this.simulationStatus.entries()) {
            if (completedStatuses.includes(status)) {
                this.stopSimulationMonitoring(simulationId);
                this.simulationStatus.delete(simulationId);
                this.activeSimulations.delete(simulationId);
            }
        }
    }

    /**
     * Export simulation data
     */
    async exportSimulationData(simulationId, format = 'json') {
        try {
            this.utils.showProgress('Exporting simulation data...');
            
            const result = await this.getSimulationResults(simulationId);
            if (!result.success) {
                this.utils.hideProgress();
                return result;
            }

            const data = result.data;
            let exportData;

            switch (format.toLowerCase()) {
                case 'json':
                    exportData = JSON.stringify(data, null, 2);
                    break;
                case 'csv':
                    exportData = this.convertToCSV(data);
                    break;
                case 'excel':
                    exportData = this.convertToExcel(data);
                    break;
                default:
                    this.utils.hideProgress();
                    return { success: false, error: 'Unsupported export format' };
            }

            // Create download link
            const blob = new Blob([exportData], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `simulation_${simulationId}_${Date.now()}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.utils.hideProgress();
            this.utils.showSuccess('Simulation data exported successfully!');
            return { success: true };
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'exportSimulationData');
        }
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV(data) {
        // Implementation for CSV conversion
        return 'CSV conversion to be implemented';
    }

    /**
     * Convert data to Excel format
     */
    convertToExcel(data) {
        // Implementation for Excel conversion
        return 'Excel conversion to be implemented';
    }
}

// Export the operations class
export default SimulationOperations; 