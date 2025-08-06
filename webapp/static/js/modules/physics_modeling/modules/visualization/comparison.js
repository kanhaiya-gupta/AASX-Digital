/**
 * Comparison Tools Module
 * Handles comparison of physics models, simulation results, and validation metrics with visualization capabilities.
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class PhysicsComparison {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        
        // Comparison types
        this.comparisonTypes = {
            MODEL: 'model',
            SIMULATION: 'simulation',
            VALIDATION: 'validation',
            PERFORMANCE: 'performance',
            PARAMETER: 'parameter'
        };
        
        // Comparison metrics
        this.metrics = {
            accuracy: {
                name: 'Accuracy',
                description: 'Model prediction accuracy',
                unit: '%',
                higherIsBetter: true
            },
            precision: {
                name: 'Precision',
                description: 'Model prediction precision',
                unit: '%',
                higherIsBetter: true
            },
            recall: {
                name: 'Recall',
                description: 'Model prediction recall',
                unit: '%',
                higherIsBetter: true
            },
            f1_score: {
                name: 'F1 Score',
                description: 'Harmonic mean of precision and recall',
                unit: '',
                higherIsBetter: true
            },
            mse: {
                name: 'Mean Squared Error',
                description: 'Mean squared error of predictions',
                unit: '',
                higherIsBetter: false
            },
            mae: {
                name: 'Mean Absolute Error',
                description: 'Mean absolute error of predictions',
                unit: '',
                higherIsBetter: false
            },
            execution_time: {
                name: 'Execution Time',
                description: 'Model execution time',
                unit: 's',
                higherIsBetter: false
            },
            memory_usage: {
                name: 'Memory Usage',
                description: 'Model memory consumption',
                unit: 'MB',
                higherIsBetter: false
            }
        };
        
        // Comparison results cache
        this.comparisonCache = new Map();
        
        // Active comparisons
        this.activeComparisons = new Map();
    }

    /**
     * Compare multiple models
     */
    async compareModels(modelIds, metrics = null, options = {}) {
        try {
            this.utils.showProgress('Comparing models...');
            
            if (!Array.isArray(modelIds) || modelIds.length < 2) {
                throw new Error('At least 2 model IDs are required for comparison');
            }

            // Use default metrics if none specified
            const comparisonMetrics = metrics || Object.keys(this.metrics);
            
            // Get model data for all models
            const modelData = await Promise.all(
                modelIds.map(id => this.api.getModel(id))
            );

            // Validate all models loaded successfully
            const failedModels = modelData.filter(result => !result.success);
            if (failedModels.length > 0) {
                throw new Error(`Failed to load ${failedModels.length} models`);
            }

            // Get validation results for all models
            const validationData = await Promise.all(
                modelIds.map(id => this.api.getValidationResults(id))
            );

            // Perform comparison
            const comparisonResults = this.performModelComparison(
                modelData.map(result => result.data),
                validationData.map(result => result.data),
                comparisonMetrics,
                options
            );

            // Cache results
            const comparisonId = this.generateComparisonId(modelIds, comparisonMetrics);
            this.comparisonCache.set(comparisonId, comparisonResults);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Model comparison completed');
            
            return comparisonResults;
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error comparing models:', error);
            this.utils.handleError(error, 'PhysicsComparison.compareModels');
            return null;
        }
    }

    /**
     * Compare simulation results
     */
    async compareSimulations(simulationIds, options = {}) {
        try {
            this.utils.showProgress('Comparing simulation results...');
            
            if (!Array.isArray(simulationIds) || simulationIds.length < 2) {
                throw new Error('At least 2 simulation IDs are required for comparison');
            }

            // Get simulation results for all simulations
            const simulationData = await Promise.all(
                simulationIds.map(id => this.api.getSimulationResults(id))
            );

            // Validate all simulations loaded successfully
            const failedSimulations = simulationData.filter(result => !result.success);
            if (failedSimulations.length > 0) {
                throw new Error(`Failed to load ${failedSimulations.length} simulation results`);
            }

            // Perform comparison
            const comparisonResults = this.performSimulationComparison(
                simulationData.map(result => result.data),
                options
            );

            // Cache results
            const comparisonId = this.generateComparisonId(simulationIds, ['simulation']);
            this.comparisonCache.set(comparisonId, comparisonResults);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Simulation comparison completed');
            
            return comparisonResults;
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error comparing simulations:', error);
            this.utils.handleError(error, 'PhysicsComparison.compareSimulations');
            return null;
        }
    }

    /**
     * Compare validation results
     */
    async compareValidations(modelIds, options = {}) {
        try {
            this.utils.showProgress('Comparing validation results...');
            
            if (!Array.isArray(modelIds) || modelIds.length < 2) {
                throw new Error('At least 2 model IDs are required for validation comparison');
            }

            // Get validation results for all models
            const validationData = await Promise.all(
                modelIds.map(id => this.api.getValidationResults(id))
            );

            // Validate all validations loaded successfully
            const failedValidations = validationData.filter(result => !result.success);
            if (failedValidations.length > 0) {
                throw new Error(`Failed to load ${failedValidations.length} validation results`);
            }

            // Perform comparison
            const comparisonResults = this.performValidationComparison(
                validationData.map(result => result.data),
                options
            );

            // Cache results
            const comparisonId = this.generateComparisonId(modelIds, ['validation']);
            this.comparisonCache.set(comparisonId, comparisonResults);
            
            this.utils.hideProgress();
            this.utils.showSuccess('Validation comparison completed');
            
            return comparisonResults;
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error comparing validations:', error);
            this.utils.handleError(error, 'PhysicsComparison.compareValidations');
            return null;
        }
    }

    /**
     * Perform model comparison
     */
    performModelComparison(modelData, validationData, metrics, options = {}) {
        const results = {
            type: this.comparisonTypes.MODEL,
            timestamp: new Date().toISOString(),
            models: modelData.map(model => ({
                id: model.id,
                name: model.name,
                type: model.physics_type,
                created_at: model.created_at
            })),
            metrics: {},
            summary: {},
            recommendations: []
        };

        // Compare each metric
        metrics.forEach(metric => {
            if (this.metrics[metric]) {
                const metricData = this.compareMetric(validationData, metric, options);
                results.metrics[metric] = metricData;
            }
        });

        // Generate summary
        results.summary = this.generateComparisonSummary(results.metrics, options);
        
        // Generate recommendations
        results.recommendations = this.generateRecommendations(results, options);

        return results;
    }

    /**
     * Perform simulation comparison
     */
    performSimulationComparison(simulationData, options = {}) {
        const results = {
            type: this.comparisonTypes.SIMULATION,
            timestamp: new Date().toISOString(),
            simulations: simulationData.map(sim => ({
                id: sim.id,
                model_id: sim.model_id,
                status: sim.status,
                duration: sim.duration,
                created_at: sim.created_at
            })),
            timeSeriesComparison: {},
            scalarComparison: {},
            performanceComparison: {},
            summary: {}
        };

        // Compare time series data
        if (simulationData.some(sim => sim.time_series)) {
            results.timeSeriesComparison = this.compareTimeSeries(simulationData, options);
        }

        // Compare scalar results
        if (simulationData.some(sim => sim.scalar_results)) {
            results.scalarComparison = this.compareScalarResults(simulationData, options);
        }

        // Compare performance metrics
        results.performanceComparison = this.comparePerformance(simulationData, options);

        // Generate summary
        results.summary = this.generateSimulationSummary(results, options);

        return results;
    }

    /**
     * Perform validation comparison
     */
    performValidationComparison(validationData, options = {}) {
        const results = {
            type: this.comparisonTypes.VALIDATION,
            timestamp: new Date().toISOString(),
            validations: validationData.map(val => ({
                model_id: val.model_id,
                accuracy_score: val.accuracy_score,
                validation_date: val.validation_date
            })),
            metrics: {},
            trends: {},
            summary: {}
        };

        // Compare validation metrics
        Object.keys(this.metrics).forEach(metric => {
            const metricData = this.compareValidationMetric(validationData, metric, options);
            if (metricData) {
                results.metrics[metric] = metricData;
            }
        });

        // Analyze trends
        results.trends = this.analyzeValidationTrends(validationData, options);

        // Generate summary
        results.summary = this.generateValidationSummary(results, options);

        return results;
    }

    /**
     * Compare a specific metric across models
     */
    compareMetric(validationData, metric, options = {}) {
        const metricInfo = this.metrics[metric];
        if (!metricInfo) return null;

        const values = validationData.map(val => {
            const metricValue = val.metrics?.[metric]?.value || val[metric] || 0;
            return {
                model_id: val.model_id,
                value: metricValue,
                unit: metricInfo.unit
            };
        });

        // Calculate statistics
        const numericValues = values.map(v => v.value).filter(v => !isNaN(v));
        const mean = numericValues.length > 0 ? numericValues.reduce((a, b) => a + b, 0) / numericValues.length : 0;
        const min = Math.min(...numericValues);
        const max = Math.max(...numericValues);
        const std = this.calculateStandardDeviation(numericValues);

        // Find best and worst models
        const sortedValues = [...values].sort((a, b) => {
            if (metricInfo.higherIsBetter) {
                return b.value - a.value;
            } else {
                return a.value - b.value;
            }
        });

        return {
            metric: metric,
            metric_name: metricInfo.name,
            description: metricInfo.description,
            unit: metricInfo.unit,
            values: values,
            statistics: {
                mean: mean,
                min: min,
                max: max,
                std: std,
                count: numericValues.length
            },
            best_model: sortedValues[0],
            worst_model: sortedValues[sortedValues.length - 1],
            ranking: sortedValues.map((v, index) => ({
                rank: index + 1,
                model_id: v.model_id,
                value: v.value
            }))
        };
    }

    /**
     * Compare time series data
     */
    compareTimeSeries(simulationData, options = {}) {
        const comparison = {
            common_time_range: null,
            series_comparison: {},
            correlation_analysis: {},
            statistical_comparison: {}
        };

        // Find common time range
        const allTimeRanges = simulationData
            .filter(sim => sim.time_series)
            .map(sim => {
                const times = sim.time_series.flatMap(series => series.data.map(point => point.time));
                return { min: Math.min(...times), max: Math.max(...times) };
            });

        if (allTimeRanges.length > 0) {
            comparison.common_time_range = {
                start: Math.max(...allTimeRanges.map(r => r.min)),
                end: Math.min(...allTimeRanges.map(r => r.max))
            };
        }

        // Compare each time series
        simulationData.forEach((sim, simIndex) => {
            if (sim.time_series) {
                sim.time_series.forEach((series, seriesIndex) => {
                    const seriesKey = `sim_${simIndex}_series_${seriesIndex}`;
                    comparison.series_comparison[seriesKey] = {
                        simulation_id: sim.id,
                        series_name: series.name,
                        data_points: series.data.length,
                        time_range: {
                            start: Math.min(...series.data.map(p => p.time)),
                            end: Math.max(...series.data.map(p => p.time))
                        },
                        statistics: this.calculateTimeSeriesStatistics(series.data)
                    };
                });
            }
        });

        return comparison;
    }

    /**
     * Compare scalar results
     */
    compareScalarResults(simulationData, options = {}) {
        const comparison = {
            common_parameters: [],
            parameter_comparison: {},
            statistical_summary: {}
        };

        // Find common parameters
        const allParameters = simulationData
            .filter(sim => sim.scalar_results)
            .flatMap(sim => sim.scalar_results.map(result => result.parameter));

        comparison.common_parameters = [...new Set(allParameters)];

        // Compare each parameter
        comparison.common_parameters.forEach(parameter => {
            const values = simulationData
                .filter(sim => sim.scalar_results)
                .map(sim => {
                    const result = sim.scalar_results.find(r => r.parameter === parameter);
                    return result ? result.value : null;
                })
                .filter(v => v !== null);

            if (values.length > 0) {
                comparison.parameter_comparison[parameter] = {
                    values: values,
                    mean: values.reduce((a, b) => a + b, 0) / values.length,
                    min: Math.min(...values),
                    max: Math.max(...values),
                    std: this.calculateStandardDeviation(values)
                };
            }
        });

        return comparison;
    }

    /**
     * Compare performance metrics
     */
    comparePerformance(simulationData, options = {}) {
        const comparison = {
            execution_time: {},
            memory_usage: {},
            resource_efficiency: {}
        };

        // Compare execution times
        const executionTimes = simulationData.map(sim => sim.duration || 0);
        comparison.execution_time = {
            values: executionTimes,
            mean: executionTimes.reduce((a, b) => a + b, 0) / executionTimes.length,
            min: Math.min(...executionTimes),
            max: Math.max(...executionTimes),
            fastest_simulation: simulationData[executionTimes.indexOf(Math.min(...executionTimes))]?.id
        };

        // Compare memory usage (if available)
        const memoryUsage = simulationData.map(sim => sim.memory_usage || 0);
        comparison.memory_usage = {
            values: memoryUsage,
            mean: memoryUsage.reduce((a, b) => a + b, 0) / memoryUsage.length,
            min: Math.min(...memoryUsage),
            max: Math.max(...memoryUsage),
            most_efficient: simulationData[memoryUsage.indexOf(Math.min(...memoryUsage))]?.id
        };

        return comparison;
    }

    /**
     * Compare validation metric
     */
    compareValidationMetric(validationData, metric, options = {}) {
        const values = validationData.map(val => {
            const metricValue = val.metrics?.[metric]?.value || val[metric] || 0;
            return {
                model_id: val.model_id,
                value: metricValue,
                validation_date: val.validation_date
            };
        });

        if (values.length === 0) return null;

        const numericValues = values.map(v => v.value).filter(v => !isNaN(v));
        
        return {
            metric: metric,
            values: values,
            statistics: {
                mean: numericValues.reduce((a, b) => a + b, 0) / numericValues.length,
                min: Math.min(...numericValues),
                max: Math.max(...numericValues),
                std: this.calculateStandardDeviation(numericValues)
            }
        };
    }

    /**
     * Analyze validation trends
     */
    analyzeValidationTrends(validationData, options = {}) {
        const trends = {
            accuracy_trend: [],
            performance_trend: [],
            overall_trend: 'stable'
        };

        // Sort by validation date
        const sortedData = validationData.sort((a, b) => 
            new Date(a.validation_date) - new Date(b.validation_date)
        );

        // Analyze accuracy trend
        if (sortedData.length > 1) {
            const accuracyValues = sortedData.map(val => val.accuracy_score || 0);
            trends.accuracy_trend = this.calculateTrend(accuracyValues);
            
            // Determine overall trend
            const firstHalf = accuracyValues.slice(0, Math.floor(accuracyValues.length / 2));
            const secondHalf = accuracyValues.slice(Math.floor(accuracyValues.length / 2));
            
            const firstHalfAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
            const secondHalfAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
            
            const change = secondHalfAvg - firstHalfAvg;
            if (Math.abs(change) < 0.01) {
                trends.overall_trend = 'stable';
            } else if (change > 0) {
                trends.overall_trend = 'improving';
            } else {
                trends.overall_trend = 'declining';
            }
        }

        return trends;
    }

    /**
     * Generate comparison summary
     */
    generateComparisonSummary(metrics, options = {}) {
        const summary = {
            total_models: 0,
            best_overall_model: null,
            worst_overall_model: null,
            average_performance: {},
            recommendations: []
        };

        if (Object.keys(metrics).length === 0) return summary;

        // Calculate overall scores
        const modelScores = new Map();
        const metricWeights = options.metricWeights || {};

        Object.entries(metrics).forEach(([metric, data]) => {
            const weight = metricWeights[metric] || 1;
            
            data.values.forEach(value => {
                const currentScore = modelScores.get(value.model_id) || 0;
                const normalizedScore = this.normalizeScore(value.value, data.statistics.min, data.statistics.max, this.metrics[metric].higherIsBetter);
                modelScores.set(value.model_id, currentScore + (normalizedScore * weight));
            });
        });

        // Find best and worst models
        const sortedScores = Array.from(modelScores.entries()).sort((a, b) => b[1] - a[1]);
        
        if (sortedScores.length > 0) {
            summary.total_models = sortedScores.length;
            summary.best_overall_model = sortedScores[0][0];
            summary.worst_overall_model = sortedScores[sortedScores.length - 1][0];
        }

        return summary;
    }

    /**
     * Generate simulation summary
     */
    generateSimulationSummary(results, options = {}) {
        return {
            total_simulations: results.simulations.length,
            successful_simulations: results.simulations.filter(s => s.status === 'completed').length,
            average_execution_time: results.performanceComparison.execution_time?.mean || 0,
            fastest_simulation: results.performanceComparison.execution_time?.fastest_simulation,
            most_efficient_simulation: results.performanceComparison.memory_usage?.most_efficient
        };
    }

    /**
     * Generate validation summary
     */
    generateValidationSummary(results, options = {}) {
        return {
            total_validations: results.validations.length,
            average_accuracy: results.validations.reduce((sum, val) => sum + (val.accuracy_score || 0), 0) / results.validations.length,
            trend: results.trends.overall_trend,
            best_accuracy: Math.max(...results.validations.map(v => v.accuracy_score || 0)),
            worst_accuracy: Math.min(...results.validations.map(v => v.accuracy_score || 0))
        };
    }

    /**
     * Generate recommendations
     */
    generateRecommendations(results, options = {}) {
        const recommendations = [];

        if (results.type === this.comparisonTypes.MODEL) {
            // Model-specific recommendations
            Object.entries(results.metrics).forEach(([metric, data]) => {
                const metricInfo = this.metrics[metric];
                const bestModel = data.best_model;
                const worstModel = data.worst_model;
                
                if (bestModel && worstModel) {
                    const improvement = Math.abs(bestModel.value - worstModel.value);
                    if (improvement > 0.1) {
                        recommendations.push({
                            type: 'performance',
                            metric: metric,
                            message: `Consider using ${bestModel.model_id} for ${metricInfo.name} (${improvement.toFixed(2)} ${metricInfo.unit} better than ${worstModel.model_id})`,
                            priority: 'medium'
                        });
                    }
                }
            });
        }

        return recommendations;
    }

    /**
     * Calculate standard deviation
     */
    calculateStandardDeviation(values) {
        if (values.length === 0) return 0;
        
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
        const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
        
        return Math.sqrt(avgSquaredDiff);
    }

    /**
     * Calculate time series statistics
     */
    calculateTimeSeriesStatistics(data) {
        if (!Array.isArray(data) || data.length === 0) return {};

        const values = data.map(point => point.value).filter(v => !isNaN(v));
        
        return {
            count: values.length,
            mean: values.reduce((a, b) => a + b, 0) / values.length,
            min: Math.min(...values),
            max: Math.max(...values),
            std: this.calculateStandardDeviation(values)
        };
    }

    /**
     * Calculate trend from values
     */
    calculateTrend(values) {
        if (values.length < 2) return 'insufficient_data';

        const n = values.length;
        const sumX = (n * (n - 1)) / 2;
        const sumY = values.reduce((a, b) => a + b, 0);
        const sumXY = values.reduce((sum, value, index) => sum + (value * index), 0);
        const sumX2 = values.reduce((sum, value, index) => sum + (index * index), 0);

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);

        if (Math.abs(slope) < 0.01) return 'stable';
        return slope > 0 ? 'increasing' : 'decreasing';
    }

    /**
     * Normalize score for comparison
     */
    normalizeScore(value, min, max, higherIsBetter) {
        if (max === min) return 0.5;
        
        const normalized = (value - min) / (max - min);
        return higherIsBetter ? normalized : 1 - normalized;
    }

    /**
     * Generate comparison ID
     */
    generateComparisonId(ids, metrics) {
        return `${ids.sort().join('_')}_${metrics.sort().join('_')}_${Date.now()}`;
    }

    /**
     * Get cached comparison results
     */
    getCachedComparison(comparisonId) {
        return this.comparisonCache.get(comparisonId);
    }

    /**
     * Clear comparison cache
     */
    clearCache() {
        this.comparisonCache.clear();
    }

    /**
     * Get available metrics
     */
    getAvailableMetrics() {
        return this.metrics;
    }

    /**
     * Get comparison types
     */
    getComparisonTypes() {
        return this.comparisonTypes;
    }

    /**
     * Export comparison results
     */
    async exportComparisonResults(comparisonId, format = 'json', options = {}) {
        const results = this.getCachedComparison(comparisonId);
        if (!results) {
            throw new Error('Comparison results not found');
        }

        // This would integrate with the export module
        // For now, return the results directly
        return results;
    }
}

// Export the comparison class
export default PhysicsComparison; 