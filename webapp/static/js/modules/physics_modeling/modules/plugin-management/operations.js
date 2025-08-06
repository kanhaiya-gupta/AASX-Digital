/**
 * Plugin Management Operations
 * Handles plugin discovery, selection, and management for physics modeling
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class PluginManagementOperations {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        this.availablePlugins = new Map();
        this.selectedPlugin = null;
        this.pluginCategories = new Set();
    }

    /**
     * Load all available plugins
     */
    async loadAvailablePlugins() {
        try {
            this.utils.showProgress('Loading available plugins...');
            
            const result = await this.api.getAvailablePlugins();
            this.utils.hideProgress();
            
            if (result.success) {
                this.availablePlugins.clear();
                this.pluginCategories.clear();
                
                result.data.forEach(plugin => {
                    this.availablePlugins.set(plugin.plugin_id, plugin);
                    this.pluginCategories.add(plugin.category);
                });
                
                console.log(`Loaded ${this.availablePlugins.size} plugins`);
                return { success: true, data: result.data };
            } else {
                this.utils.showError('Failed to load plugins');
                return { success: false, error: result.error };
            }
        } catch (error) {
            this.utils.hideProgress();
            return this.utils.handleError(error, 'loadAvailablePlugins');
        }
    }

    /**
     * Get plugins for a specific digital twin
     */
    async getPluginsForTwin(twinId) {
        try {
            const result = await this.api.getPluginsForTwin(twinId);
            
            if (result.success) {
                return { success: true, data: result.data };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return this.utils.handleError(error, 'getPluginsForTwin');
        }
    }

    /**
     * Get plugin details
     */
    async getPluginDetails(pluginId) {
        try {
            const result = await this.api.getPluginDetails(pluginId);
            
            if (result.success) {
                return { success: true, data: result.data };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return this.utils.handleError(error, 'getPluginDetails');
        }
    }

    /**
     * Select a plugin for simulation
     */
    selectPlugin(pluginId) {
        const plugin = this.availablePlugins.get(pluginId);
        if (plugin) {
            this.selectedPlugin = plugin;
            console.log(`Selected plugin: ${plugin.name} (${plugin.plugin_id})`);
            return { success: true, data: plugin };
        } else {
            console.error(`Plugin not found: ${pluginId}`);
            return { success: false, error: 'Plugin not found' };
        }
    }

    /**
     * Get selected plugin
     */
    getSelectedPlugin() {
        return this.selectedPlugin;
    }

    /**
     * Get plugins by category
     */
    getPluginsByCategory(category) {
        return Array.from(this.availablePlugins.values())
            .filter(plugin => plugin.category === category);
    }

    /**
     * Get all plugin categories
     */
    getPluginCategories() {
        return Array.from(this.pluginCategories);
    }

    /**
     * Validate plugin parameters
     */
    validatePluginParameters(pluginId, parameters) {
        const plugin = this.availablePlugins.get(pluginId);
        if (!plugin) {
            return { isValid: false, errors: ['Plugin not found'] };
        }

        const errors = [];
        const requiredParams = plugin.parameters.filter(param => param.required);

        // Check required parameters
        requiredParams.forEach(param => {
            if (!(param.name in parameters)) {
                errors.push(`Missing required parameter: ${param.name}`);
            }
        });

        // Validate parameter types and ranges
        plugin.parameters.forEach(param => {
            if (param.name in parameters) {
                const value = parameters[param.name];
                
                // Type validation
                if (param.parameter_type === 'SCALAR' && typeof value !== 'number') {
                    errors.push(`Parameter ${param.name} must be a number`);
                }
                
                // Range validation
                if (param.min_value !== null && value < param.min_value) {
                    errors.push(`Parameter ${param.name} must be >= ${param.min_value}`);
                }
                if (param.max_value !== null && value > param.max_value) {
                    errors.push(`Parameter ${param.name} must be <= ${param.max_value}`);
                }
            }
        });

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Get default parameters for a plugin
     */
    getDefaultParameters(pluginId) {
        const plugin = this.availablePlugins.get(pluginId);
        if (!plugin) {
            return {};
        }

        const defaults = {};
        plugin.parameters.forEach(param => {
            if (param.default_value !== null) {
                defaults[param.name] = param.default_value;
            }
        });

        return defaults;
    }

    /**
     * Create plugin selection UI
     */
    createPluginSelectionUI(container, onPluginSelect) {
        if (this.availablePlugins.size === 0) {
            container.innerHTML = '<p class="text-muted">No plugins available</p>';
            return;
        }

        const categories = this.getPluginCategories();
        let html = '<div class="row">';

        categories.forEach(category => {
            const plugins = this.getPluginsByCategory(category);
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-puzzle-piece me-2"></i>${category.charAt(0).toUpperCase() + category.slice(1)}
                            </h6>
                        </div>
                                                 <div class="card-body">
                             <div class="d-flex flex-column">
            `;

            plugins.forEach(plugin => {
                html += `
                    <div class="plugin-select-btn" 
                         data-plugin-id="${plugin.plugin_id}"
                         style="padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; cursor: pointer; background-color: white; color: black; outline: none; -webkit-tap-highlight-color: transparent;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${plugin.name}</strong>
                                <br><small style="color: #666;">${plugin.description}</small>
                            </div>
                            <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">v${plugin.version}</span>
                        </div>
                    </div>
                `;
            });

            html += `
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;

        // Add event listeners
        container.querySelectorAll('.plugin-select-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const pluginId = e.currentTarget.dataset.pluginId;
                if (onPluginSelect) {
                    onPluginSelect(pluginId);
                }
            });
        });
    }

    /**
     * Create plugin details UI
     */
    createPluginDetailsUI(container, pluginId) {
        const plugin = this.availablePlugins.get(pluginId);
        if (!plugin) {
            container.innerHTML = '<p class="text-danger">Plugin not found</p>';
            return;
        }

        let html = `
            <div class="row">
                <div class="col-md-8">
                    <h5>${plugin.name}</h5>
                    <p class="text-muted">${plugin.description}</p>
                    
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <strong>Category:</strong><br>
                            <span class="badge bg-secondary">${plugin.category}</span>
                        </div>
                        <div class="col-md-3">
                            <strong>Version:</strong><br>
                            <span class="badge bg-info">${plugin.version}</span>
                        </div>
                        <div class="col-md-6">
                            <strong>Plugin ID:</strong><br>
                            <code>${plugin.plugin_id}</code>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Parameters section
        if (plugin.parameters && plugin.parameters.length > 0) {
            html += `
                <div class="mt-4">
                    <h6>Parameters</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Default</th>
                                    <th>Required</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            plugin.parameters.forEach(param => {
                html += `
                    <tr>
                        <td><code>${param.name}</code></td>
                        <td><span class="badge bg-light text-dark">${param.parameter_type}</span></td>
                        <td>${param.default_value !== null ? param.default_value : '-'}</td>
                        <td>${param.required ? '<span class="text-success">✓</span>' : '<span class="text-muted">-</span>'}</td>
                        <td>${param.description || '-'}</td>
                    </tr>
                `;
            });

            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Equations section
        if (plugin.equations && plugin.equations.length > 0) {
            html += `
                <div class="mt-4">
                    <h6>Equations</h6>
                    <div class="list-group">
            `;

            plugin.equations.forEach(eq => {
                html += `
                    <div class="list-group-item">
                        <h6 class="mb-1">${eq.name}</h6>
                        <p class="mb-1"><code>${eq.equation}</code></p>
                        <small class="text-muted">${eq.description || ''}</small>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    }
}

export default PluginManagementOperations; 