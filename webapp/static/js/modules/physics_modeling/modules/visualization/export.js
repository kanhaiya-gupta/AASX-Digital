/**
 * Export Module
 * Handles data export functionality for physics simulation results and visualizations
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class PhysicsExport {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        
        // Export formats
        this.formats = {
            CSV: 'csv',
            JSON: 'json',
            EXCEL: 'xlsx',
            PNG: 'png',
            PDF: 'pdf',
            GLTF: 'gltf',
            GLB: 'glb'
        };
        
        // Export templates
        this.templates = {
            simulation_results: {
                name: 'Simulation Results',
                description: 'Export simulation results with metadata',
                fields: ['timestamp', 'model_id', 'parameters', 'results', 'metadata']
            },
            model_comparison: {
                name: 'Model Comparison',
                description: 'Export model comparison data',
                fields: ['model_ids', 'comparison_metrics', 'validation_results', 'performance_data']
            },
            validation_report: {
                name: 'Validation Report',
                description: 'Export model validation report',
                fields: ['model_id', 'validation_metrics', 'accuracy_scores', 'recommendations']
            },
            time_series: {
                name: 'Time Series Data',
                description: 'Export time series simulation data',
                fields: ['time', 'values', 'parameters', 'metadata']
            }
        };
    }

    /**
     * Export simulation results
     */
    async exportSimulationResults(simulationId, format = 'csv', options = {}) {
        try {
            this.utils.showProgress('Preparing simulation results for export...');
            
            // Get simulation results
            const results = await this.api.getSimulationResults(simulationId);
            
            if (!results.success) {
                throw new Error('Failed to load simulation results');
            }

            // Process data based on format
            let exportData;
            let filename;
            
            switch (format.toLowerCase()) {
                case 'csv':
                    exportData = this.convertToCSV(results.data, options);
                    filename = `simulation_results_${simulationId}_${Date.now()}.csv`;
                    break;
                case 'json':
                    exportData = this.convertToJSON(results.data, options);
                    filename = `simulation_results_${simulationId}_${Date.now()}.json`;
                    break;
                case 'xlsx':
                    exportData = await this.convertToExcel(results.data, options);
                    filename = `simulation_results_${simulationId}_${Date.now()}.xlsx`;
                    break;
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }

            // Trigger download
            this.downloadFile(exportData, filename, format);
            
            this.utils.hideProgress();
            this.utils.showSuccess(`Simulation results exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error exporting simulation results:', error);
            this.utils.handleError(error, 'PhysicsExport.exportSimulationResults');
        }
    }

    /**
     * Export model comparison data
     */
    async exportModelComparison(modelIds, format = 'csv', options = {}) {
        try {
            this.utils.showProgress('Preparing model comparison for export...');
            
            // Get comparison data
            const comparisonData = await this.api.compareModels(modelIds);
            
            if (!comparisonData.success) {
                throw new Error('Failed to load model comparison data');
            }

            // Process data based on format
            let exportData;
            let filename;
            
            switch (format.toLowerCase()) {
                case 'csv':
                    exportData = this.convertComparisonToCSV(comparisonData.data, options);
                    filename = `model_comparison_${Date.now()}.csv`;
                    break;
                case 'json':
                    exportData = this.convertToJSON(comparisonData.data, options);
                    filename = `model_comparison_${Date.now()}.json`;
                    break;
                case 'xlsx':
                    exportData = await this.convertComparisonToExcel(comparisonData.data, options);
                    filename = `model_comparison_${Date.now()}.xlsx`;
                    break;
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }

            // Trigger download
            this.downloadFile(exportData, filename, format);
            
            this.utils.hideProgress();
            this.utils.showSuccess(`Model comparison exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error exporting model comparison:', error);
            this.utils.handleError(error, 'PhysicsExport.exportModelComparison');
        }
    }

    /**
     * Export validation report
     */
    async exportValidationReport(modelId, format = 'pdf', options = {}) {
        try {
            this.utils.showProgress('Generating validation report...');
            
            // Get validation data
            const validationData = await this.api.getValidationResults(modelId);
            
            if (!validationData.success) {
                throw new Error('Failed to load validation data');
            }

            // Generate report based on format
            let exportData;
            let filename;
            
            switch (format.toLowerCase()) {
                case 'pdf':
                    exportData = await this.generatePDFReport(validationData.data, options);
                    filename = `validation_report_${modelId}_${Date.now()}.pdf`;
                    break;
                case 'json':
                    exportData = this.convertToJSON(validationData.data, options);
                    filename = `validation_report_${modelId}_${Date.now()}.json`;
                    break;
                case 'csv':
                    exportData = this.convertValidationToCSV(validationData.data, options);
                    filename = `validation_report_${modelId}_${Date.now()}.csv`;
                    break;
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }

            // Trigger download
            this.downloadFile(exportData, filename, format);
            
            this.utils.hideProgress();
            this.utils.showSuccess(`Validation report exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error exporting validation report:', error);
            this.utils.handleError(error, 'PhysicsExport.exportValidationReport');
        }
    }

    /**
     * Export chart as image
     */
    exportChartAsImage(chartInstance, format = 'png', options = {}) {
        try {
            if (!chartInstance || !chartInstance.canvas) {
                throw new Error('Invalid chart instance');
            }

            const canvas = chartInstance.canvas;
            const filename = `physics_chart_${Date.now()}.${format}`;
            
            // Convert canvas to blob
            canvas.toBlob((blob) => {
                this.downloadBlob(blob, filename);
            }, `image/${format}`, options.quality || 0.9);
            
            this.utils.showSuccess(`Chart exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            console.error('Error exporting chart:', error);
            this.utils.handleError(error, 'PhysicsExport.exportChartAsImage');
        }
    }

    /**
     * Export 3D model
     */
    async export3DModel(modelId, format = 'gltf', options = {}) {
        try {
            this.utils.showProgress('Preparing 3D model for export...');
            
            // Get model data
            const modelData = await this.api.getModel(modelId);
            
            if (!modelData.success) {
                throw new Error('Failed to load model data');
            }

            // Convert to 3D format
            let exportData;
            let filename;
            
            switch (format.toLowerCase()) {
                case 'gltf':
                case 'glb':
                    exportData = await this.convertToGLTF(modelData.data, format === 'glb', options);
                    filename = `physics_model_${modelId}_${Date.now()}.${format}`;
                    break;
                case 'obj':
                    exportData = await this.convertToOBJ(modelData.data, options);
                    filename = `physics_model_${modelId}_${Date.now()}.obj`;
                    break;
                default:
                    throw new Error(`Unsupported 3D format: ${format}`);
            }

            // Trigger download
            this.downloadFile(exportData, filename, format);
            
            this.utils.hideProgress();
            this.utils.showSuccess(`3D model exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error exporting 3D model:', error);
            this.utils.handleError(error, 'PhysicsExport.export3DModel');
        }
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV(data, options = {}) {
        const { includeHeaders = true, delimiter = ',', flatten = false } = options;
        
        if (flatten) {
            return this.flattenToCSV(data, includeHeaders, delimiter);
        }

        // Handle time series data
        if (data.time_series) {
            return this.convertTimeSeriesToCSV(data.time_series, includeHeaders, delimiter);
        }

        // Handle scalar results
        if (data.scalar_results) {
            return this.convertScalarResultsToCSV(data.scalar_results, includeHeaders, delimiter);
        }

        // Handle general data
        return this.convertGeneralDataToCSV(data, includeHeaders, delimiter);
    }

    /**
     * Convert time series data to CSV
     */
    convertTimeSeriesToCSV(timeSeries, includeHeaders = true, delimiter = ',') {
        if (!Array.isArray(timeSeries) || timeSeries.length === 0) {
            return '';
        }

        let csv = '';
        
        if (includeHeaders) {
            csv += `Time${delimiter}`;
            timeSeries.forEach((series, index) => {
                csv += `${series.name || `Series_${index + 1}`}${delimiter}`;
            });
            csv = csv.slice(0, -1) + '\n';
        }

        // Find the maximum length of all series
        const maxLength = Math.max(...timeSeries.map(series => series.data.length));
        
        for (let i = 0; i < maxLength; i++) {
            const time = timeSeries[0]?.data[i]?.time || i;
            csv += `${time}${delimiter}`;
            
            timeSeries.forEach(series => {
                const value = series.data[i]?.value || '';
                csv += `${value}${delimiter}`;
            });
            
            csv = csv.slice(0, -1) + '\n';
        }

        return csv;
    }

    /**
     * Convert scalar results to CSV
     */
    convertScalarResultsToCSV(scalarResults, includeHeaders = true, delimiter = ',') {
        if (!Array.isArray(scalarResults) || scalarResults.length === 0) {
            return '';
        }

        let csv = '';
        
        if (includeHeaders) {
            csv += `Parameter${delimiter}Value${delimiter}Unit${delimiter}Description\n`;
        }

        scalarResults.forEach(result => {
            csv += `${result.parameter || ''}${delimiter}`;
            csv += `${result.value || ''}${delimiter}`;
            csv += `${result.unit || ''}${delimiter}`;
            csv += `${result.description || ''}\n`;
        });

        return csv;
    }

    /**
     * Convert general data to CSV
     */
    convertGeneralDataToCSV(data, includeHeaders = true, delimiter = ',') {
        if (typeof data !== 'object' || data === null) {
            return '';
        }

        const rows = this.objectToRows(data);
        
        if (rows.length === 0) {
            return '';
        }

        let csv = '';
        
        if (includeHeaders) {
            const headers = Object.keys(rows[0]);
            csv += headers.join(delimiter) + '\n';
        }

        rows.forEach(row => {
            const values = Object.values(row).map(value => {
                if (typeof value === 'string' && value.includes(delimiter)) {
                    return `"${value}"`;
                }
                return value;
            });
            csv += values.join(delimiter) + '\n';
        });

        return csv;
    }

    /**
     * Convert object to rows for CSV
     */
    objectToRows(obj, prefix = '') {
        const rows = [];
        
        for (const [key, value] of Object.entries(obj)) {
            const fullKey = prefix ? `${prefix}.${key}` : key;
            
            if (value === null || value === undefined) {
                rows.push({ [fullKey]: '' });
            } else if (typeof value === 'object' && !Array.isArray(value)) {
                rows.push(...this.objectToRows(value, fullKey));
            } else if (Array.isArray(value)) {
                value.forEach((item, index) => {
                    if (typeof item === 'object' && item !== null) {
                        rows.push(...this.objectToRows(item, `${fullKey}[${index}]`));
                    } else {
                        rows.push({ [`${fullKey}[${index}]`]: item });
                    }
                });
            } else {
                rows.push({ [fullKey]: value });
            }
        }
        
        return rows;
    }

    /**
     * Convert data to JSON format
     */
    convertToJSON(data, options = {}) {
        const { pretty = true, includeMetadata = true } = options;
        
        const exportData = {
            timestamp: new Date().toISOString(),
            data: data
        };
        
        if (includeMetadata) {
            exportData.metadata = {
                exportFormat: 'json',
                version: '1.0',
                generatedBy: 'Physics Modeling Export Module'
            };
        }
        
        return pretty ? JSON.stringify(exportData, null, 2) : JSON.stringify(exportData);
    }

    /**
     * Convert data to Excel format
     */
    async convertToExcel(data, options = {}) {
        try {
            // Check if XLSX library is available
            if (typeof XLSX === 'undefined') {
                throw new Error('XLSX library is not loaded. Please include SheetJS in your HTML.');
            }

            const { sheets = ['Data'], includeCharts = false } = options;
            
            const workbook = XLSX.utils.book_new();
            
            // Convert data to worksheet
            const worksheet = XLSX.utils.json_to_sheet(this.flattenData(data));
            
            // Add worksheet to workbook
            XLSX.utils.book_append_sheet(workbook, worksheet, sheets[0]);
            
            // Generate Excel file
            const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            
            return new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            
        } catch (error) {
            console.error('Error converting to Excel:', error);
            throw error;
        }
    }

    /**
     * Convert comparison data to CSV
     */
    convertComparisonToCSV(comparisonData, options = {}) {
        const { includeHeaders = true, delimiter = ',' } = options;
        
        let csv = '';
        
        if (includeHeaders) {
            csv += `Metric${delimiter}Model_1${delimiter}Model_2${delimiter}Difference${delimiter}Percentage\n`;
        }

        if (comparisonData.metrics) {
            Object.entries(comparisonData.metrics).forEach(([metric, values]) => {
                const model1Value = values.model1 || '';
                const model2Value = values.model2 || '';
                const difference = values.difference || '';
                const percentage = values.percentage || '';
                
                csv += `${metric}${delimiter}${model1Value}${delimiter}${model2Value}${delimiter}${difference}${delimiter}${percentage}\n`;
            });
        }

        return csv;
    }

    /**
     * Convert comparison data to Excel
     */
    async convertComparisonToExcel(comparisonData, options = {}) {
        try {
            if (typeof XLSX === 'undefined') {
                throw new Error('XLSX library is not loaded.');
            }

            const workbook = XLSX.utils.book_new();
            
            // Create comparison sheet
            const comparisonSheet = XLSX.utils.json_to_sheet(
                Object.entries(comparisonData.metrics || {}).map(([metric, values]) => ({
                    Metric: metric,
                    Model_1: values.model1 || '',
                    Model_2: values.model2 || '',
                    Difference: values.difference || '',
                    Percentage: values.percentage || ''
                }))
            );
            
            XLSX.utils.book_append_sheet(workbook, comparisonSheet, 'Comparison');
            
            // Create summary sheet
            const summarySheet = XLSX.utils.json_to_sheet([
                { Summary: 'Model Comparison Report' },
                { 'Generated': new Date().toISOString() },
                { 'Total Metrics': Object.keys(comparisonData.metrics || {}).length },
                { 'Best Model': comparisonData.best_model || 'N/A' },
                { 'Overall Score': comparisonData.overall_score || 'N/A' }
            ]);
            
            XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');
            
            const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            return new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            
        } catch (error) {
            console.error('Error converting comparison to Excel:', error);
            throw error;
        }
    }

    /**
     * Convert validation data to CSV
     */
    convertValidationToCSV(validationData, options = {}) {
        const { includeHeaders = true, delimiter = ',' } = options;
        
        let csv = '';
        
        if (includeHeaders) {
            csv += `Metric${delimiter}Value${delimiter}Threshold${delimiter}Status${delimiter}Description\n`;
        }

        if (validationData.metrics) {
            Object.entries(validationData.metrics).forEach(([metric, data]) => {
                csv += `${metric}${delimiter}`;
                csv += `${data.value || ''}${delimiter}`;
                csv += `${data.threshold || ''}${delimiter}`;
                csv += `${data.status || ''}${delimiter}`;
                csv += `${data.description || ''}\n`;
            });
        }

        return csv;
    }

    /**
     * Generate PDF report
     */
    async generatePDFReport(validationData, options = {}) {
        try {
            // Check if jsPDF is available
            if (typeof jsPDF === 'undefined') {
                throw new Error('jsPDF library is not loaded. Please include jsPDF in your HTML.');
            }

            const { title = 'Validation Report', includeCharts = false } = options;
            
            const doc = new jsPDF();
            
            // Add title
            doc.setFontSize(20);
            doc.text(title, 20, 20);
            
            // Add timestamp
            doc.setFontSize(12);
            doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
            
            // Add validation metrics
            doc.setFontSize(14);
            doc.text('Validation Metrics:', 20, 50);
            
            let yPosition = 60;
            if (validationData.metrics) {
                Object.entries(validationData.metrics).forEach(([metric, data]) => {
                    doc.setFontSize(12);
                    doc.text(`${metric}: ${data.value} (${data.status})`, 30, yPosition);
                    yPosition += 10;
                    
                    if (yPosition > 280) {
                        doc.addPage();
                        yPosition = 20;
                    }
                });
            }
            
            // Add recommendations
            if (validationData.recommendations) {
                doc.addPage();
                doc.setFontSize(14);
                doc.text('Recommendations:', 20, 20);
                
                yPosition = 30;
                validationData.recommendations.forEach(recommendation => {
                    doc.setFontSize(12);
                    doc.text(`• ${recommendation}`, 30, yPosition);
                    yPosition += 10;
                    
                    if (yPosition > 280) {
                        doc.addPage();
                        yPosition = 20;
                    }
                });
            }
            
            return doc.output('blob');
            
        } catch (error) {
            console.error('Error generating PDF report:', error);
            throw error;
        }
    }

    /**
     * Convert model data to GLTF format
     */
    async convertToGLTF(modelData, binary = false, options = {}) {
        try {
            // This would use Three.js GLTFExporter
            // For now, return a placeholder
            const gltfData = {
                asset: {
                    version: "2.0",
                    generator: "Physics Modeling Export Module"
                },
                scene: 0,
                scenes: [{
                    nodes: [0]
                }],
                nodes: [{
                    mesh: 0
                }],
                meshes: [{
                    primitives: [{
                        attributes: {
                            POSITION: 0
                        },
                        indices: 1
                    }]
                }],
                accessors: [],
                bufferViews: [],
                buffers: []
            };
            
            return binary ? this.convertToGLB(gltfData) : JSON.stringify(gltfData, null, 2);
            
        } catch (error) {
            console.error('Error converting to GLTF:', error);
            throw error;
        }
    }

    /**
     * Convert to GLB (binary GLTF)
     */
    convertToGLB(gltfData) {
        // This would convert GLTF JSON to binary format
        // For now, return the JSON as a blob
        return new Blob([JSON.stringify(gltfData)], { type: 'model/gltf-binary' });
    }

    /**
     * Convert to OBJ format
     */
    async convertToOBJ(modelData, options = {}) {
        try {
            // This would convert model data to OBJ format
            // For now, return a placeholder
            let obj = '# Physics Model Export\n';
            obj += `# Generated: ${new Date().toISOString()}\n`;
            obj += `# Model: ${modelData.name || 'Unknown'}\n\n`;
            
            // Add vertices, faces, etc.
            obj += 'v 0.0 0.0 0.0\n';
            obj += 'v 1.0 0.0 0.0\n';
            obj += 'v 0.0 1.0 0.0\n';
            obj += 'f 1 2 3\n';
            
            return obj;
            
        } catch (error) {
            console.error('Error converting to OBJ:', error);
            throw error;
        }
    }

    /**
     * Flatten data for Excel export
     */
    flattenData(data) {
        const flattened = [];
        
        if (Array.isArray(data)) {
            data.forEach((item, index) => {
                flattened.push({ index, ...this.flattenObject(item) });
            });
        } else {
            flattened.push(this.flattenObject(data));
        }
        
        return flattened;
    }

    /**
     * Flatten object for export
     */
    flattenObject(obj, prefix = '') {
        const flattened = {};
        
        for (const [key, value] of Object.entries(obj)) {
            const fullKey = prefix ? `${prefix}_${key}` : key;
            
            if (value === null || value === undefined) {
                flattened[fullKey] = '';
            } else if (typeof value === 'object' && !Array.isArray(value)) {
                Object.assign(flattened, this.flattenObject(value, fullKey));
            } else if (Array.isArray(value)) {
                value.forEach((item, index) => {
                    if (typeof item === 'object' && item !== null) {
                        Object.assign(flattened, this.flattenObject(item, `${fullKey}_${index}`));
                    } else {
                        flattened[`${fullKey}_${index}`] = item;
                    }
                });
            } else {
                flattened[fullKey] = value;
            }
        }
        
        return flattened;
    }

    /**
     * Download file
     */
    downloadFile(data, filename, format) {
        let blob;
        
        if (data instanceof Blob) {
            blob = data;
        } else if (typeof data === 'string') {
            const mimeType = this.getMimeType(format);
            blob = new Blob([data], { type: mimeType });
        } else {
            blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        }
        
        this.downloadBlob(blob, filename);
    }

    /**
     * Download blob
     */
    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Get MIME type for format
     */
    getMimeType(format) {
        const mimeTypes = {
            'csv': 'text/csv',
            'json': 'application/json',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'pdf': 'application/pdf',
            'gltf': 'model/gltf+json',
            'glb': 'model/gltf-binary',
            'obj': 'text/plain'
        };
        
        return mimeTypes[format.toLowerCase()] || 'application/octet-stream';
    }

    /**
     * Get available export formats
     */
    getAvailableFormats() {
        return this.formats;
    }

    /**
     * Get export templates
     */
    getExportTemplates() {
        return this.templates;
    }

    /**
     * Create custom export template
     */
    createExportTemplate(name, description, fields) {
        this.templates[name] = {
            name,
            description,
            fields
        };
        
        return this.templates[name];
    }
}

// Export the export class
export default PhysicsExport; 