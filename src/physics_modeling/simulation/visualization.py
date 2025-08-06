"""
Visualization for physics modeling framework.

This module provides common visualization capabilities that all
physics simulations can use for result visualization.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Visualization:
    """
    Common visualization for all simulations.
    
    This class provides shared functionality for visualizing simulation results:
    - Chart generation
    - Plot creation
    - Data visualization
    - Export visualization
    """
    
    def __init__(self):
        """Initialize the visualization component."""
        logger.debug("Visualization component initialized")
    
    def create_charts(self, results: Dict[str, Any], chart_types: List[str] = None) -> Dict[str, Any]:
        """
        Create charts from simulation results.
        
        Args:
            results: Simulation results
            chart_types: List of chart types to create
            
        Returns:
            Chart data and configurations
        """
        try:
            if chart_types is None:
                chart_types = ['summary', 'numerical', 'categorical']
            
            charts = {
                'timestamp': datetime.now().isoformat(),
                'charts': {}
            }
            
            for chart_type in chart_types:
                if chart_type == 'summary':
                    charts['charts']['summary'] = self._create_summary_chart(results)
                elif chart_type == 'numerical':
                    charts['charts']['numerical'] = self._create_numerical_charts(results)
                elif chart_type == 'categorical':
                    charts['charts']['categorical'] = self._create_categorical_charts(results)
                elif chart_type == 'timeline':
                    charts['charts']['timeline'] = self._create_timeline_chart(results)
            
            logger.debug(f"Created {len(charts['charts'])} chart types")
            return charts
            
        except Exception as e:
            logger.error(f"Failed to create charts: {e}")
            return {'error': f"Chart creation failed: {str(e)}"}
    
    def _create_summary_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary chart."""
        try:
            # Extract basic statistics
            total_results = len(results.get('processed_results', {}))
            numerical_count = 0
            categorical_count = 0
            
            for result in results.get('processed_results', {}).values():
                if result.get('data_type') in ['int', 'float']:
                    numerical_count += 1
                elif result.get('data_type') == 'str':
                    categorical_count += 1
            
            return {
                'type': 'summary',
                'chart_type': 'pie',
                'data': {
                    'labels': ['Numerical', 'Categorical', 'Other'],
                    'values': [numerical_count, categorical_count, total_results - numerical_count - categorical_count],
                    'colors': ['#FF6384', '#36A2EB', '#FFCE56']
                },
                'options': {
                    'title': 'Result Types Distribution',
                    'responsive': True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create summary chart: {e}")
            return {'error': f"Summary chart creation failed: {str(e)}"}
    
    def _create_numerical_charts(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create numerical charts."""
        try:
            numerical_data = {}
            
            # Extract numerical results
            for key, result in results.get('processed_results', {}).items():
                if result.get('data_type') in ['int', 'float']:
                    value = result.get('processed_value', 0)
                    if isinstance(value, (int, float)):
                        numerical_data[key] = value
            
            if not numerical_data:
                return {'note': 'No numerical data available for charts'}
            
            charts = {
                'type': 'numerical',
                'charts': {}
            }
            
            # Bar chart of numerical values
            charts['charts']['bar'] = {
                'type': 'bar',
                'data': {
                    'labels': list(numerical_data.keys()),
                    'values': list(numerical_data.values()),
                    'colors': ['#36A2EB'] * len(numerical_data)
                },
                'options': {
                    'title': 'Numerical Results',
                    'x_label': 'Result Keys',
                    'y_label': 'Values'
                }
            }
            
            # Histogram if we have enough data
            if len(numerical_data) > 5:
                values = list(numerical_data.values())
                charts['charts']['histogram'] = {
                    'type': 'histogram',
                    'data': {
                        'values': values,
                        'bins': min(10, len(values))
                    },
                    'options': {
                        'title': 'Value Distribution',
                        'x_label': 'Values',
                        'y_label': 'Frequency'
                    }
                }
            
            return charts
            
        except Exception as e:
            logger.error(f"Failed to create numerical charts: {e}")
            return {'error': f"Numerical charts creation failed: {str(e)}"}
    
    def _create_categorical_charts(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create categorical charts."""
        try:
            categorical_data = {}
            
            # Extract categorical results
            for key, result in results.get('processed_results', {}).items():
                if result.get('data_type') == 'str':
                    value = result.get('processed_value', '')
                    if isinstance(value, str):
                        categorical_data[key] = value
            
            if not categorical_data:
                return {'note': 'No categorical data available for charts'}
            
            charts = {
                'type': 'categorical',
                'charts': {}
            }
            
            # Bar chart of categorical values
            charts['charts']['bar'] = {
                'type': 'bar',
                'data': {
                    'labels': list(categorical_data.keys()),
                    'values': [len(str(v)) for v in categorical_data.values()],  # Use length as proxy
                    'colors': ['#FF6384'] * len(categorical_data)
                },
                'options': {
                    'title': 'Categorical Results (by length)',
                    'x_label': 'Result Keys',
                    'y_label': 'String Length'
                }
            }
            
            # Pie chart of unique values
            unique_values = list(set(categorical_data.values()))
            if len(unique_values) <= 10:  # Only if we have reasonable number of unique values
                value_counts = {}
                for value in categorical_data.values():
                    value_counts[value] = value_counts.get(value, 0) + 1
                
                charts['charts']['pie'] = {
                    'type': 'pie',
                    'data': {
                        'labels': list(value_counts.keys()),
                        'values': list(value_counts.values()),
                        'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'] * 2
                    },
                    'options': {
                        'title': 'Unique Values Distribution'
                    }
                }
            
            return charts
            
        except Exception as e:
            logger.error(f"Failed to create categorical charts: {e}")
            return {'error': f"Categorical charts creation failed: {str(e)}"}
    
    def _create_timeline_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create timeline chart."""
        try:
            # Look for timestamp data in results
            timeline_data = []
            
            for key, result in results.get('processed_results', {}).items():
                value = result.get('processed_value', '')
                if isinstance(value, str) and 'timestamp' in key.lower():
                    timeline_data.append({
                        'key': key,
                        'timestamp': value,
                        'value': value
                    })
            
            if not timeline_data:
                return {'note': 'No timeline data available for charts'}
            
            return {
                'type': 'timeline',
                'chart_type': 'line',
                'data': {
                    'labels': [item['key'] for item in timeline_data],
                    'values': [item['value'] for item in timeline_data],
                    'timestamps': [item['timestamp'] for item in timeline_data]
                },
                'options': {
                    'title': 'Timeline Results',
                    'x_label': 'Time',
                    'y_label': 'Values'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create timeline chart: {e}")
            return {'error': f"Timeline chart creation failed: {str(e)}"}
    
    def generate_plot_data(self, results: Dict[str, Any], plot_type: str = 'scatter') -> Dict[str, Any]:
        """
        Generate plot data for visualization.
        
        Args:
            results: Simulation results
            plot_type: Type of plot to generate
            
        Returns:
            Plot data
        """
        try:
            if plot_type == 'scatter':
                return self._generate_scatter_plot_data(results)
            elif plot_type == 'line':
                return self._generate_line_plot_data(results)
            elif plot_type == 'heatmap':
                return self._generate_heatmap_data(results)
            else:
                logger.warning(f"Unsupported plot type: {plot_type}")
                return {'error': f"Unsupported plot type: {plot_type}"}
                
        except Exception as e:
            logger.error(f"Failed to generate plot data: {e}")
            return {'error': f"Plot data generation failed: {str(e)}"}
    
    def _generate_scatter_plot_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scatter plot data."""
        try:
            numerical_data = {}
            
            # Extract numerical results
            for key, result in results.get('processed_results', {}).items():
                if result.get('data_type') in ['int', 'float']:
                    value = result.get('processed_value', 0)
                    if isinstance(value, (int, float)):
                        numerical_data[key] = value
            
            if len(numerical_data) < 2:
                return {'error': 'Insufficient numerical data for scatter plot'}
            
            # Create x, y pairs
            keys = list(numerical_data.keys())
            values = list(numerical_data.values())
            
            return {
                'type': 'scatter',
                'data': {
                    'x': keys,
                    'y': values,
                    'labels': keys
                },
                'options': {
                    'title': 'Numerical Results Scatter Plot',
                    'x_label': 'Result Keys',
                    'y_label': 'Values'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate scatter plot data: {e}")
            return {'error': f"Scatter plot data generation failed: {str(e)}"}
    
    def _generate_line_plot_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate line plot data."""
        try:
            # This would typically be used for time series data
            # For now, we'll create a simple line plot of numerical values
            numerical_data = {}
            
            for key, result in results.get('processed_results', {}).items():
                if result.get('data_type') in ['int', 'float']:
                    value = result.get('processed_value', 0)
                    if isinstance(value, (int, float)):
                        numerical_data[key] = value
            
            if len(numerical_data) < 2:
                return {'error': 'Insufficient numerical data for line plot'}
            
            keys = list(numerical_data.keys())
            values = list(numerical_data.values())
            
            return {
                'type': 'line',
                'data': {
                    'x': keys,
                    'y': values,
                    'labels': keys
                },
                'options': {
                    'title': 'Numerical Results Line Plot',
                    'x_label': 'Result Keys',
                    'y_label': 'Values'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate line plot data: {e}")
            return {'error': f"Line plot data generation failed: {str(e)}"}
    
    def _generate_heatmap_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate heatmap data."""
        try:
            # Create a simple heatmap from numerical data
            numerical_data = {}
            
            for key, result in results.get('processed_results', {}).items():
                if result.get('data_type') in ['int', 'float']:
                    value = result.get('processed_value', 0)
                    if isinstance(value, (int, float)):
                        numerical_data[key] = value
            
            if len(numerical_data) < 4:
                return {'error': 'Insufficient numerical data for heatmap'}
            
            # Create a simple 2D representation
            keys = list(numerical_data.keys())
            values = list(numerical_data.values())
            
            # Try to create a square-ish matrix
            import math
            size = math.ceil(math.sqrt(len(values)))
            
            matrix = []
            for i in range(size):
                row = []
                for j in range(size):
                    index = i * size + j
                    if index < len(values):
                        row.append(values[index])
                    else:
                        row.append(0)
                matrix.append(row)
            
            return {
                'type': 'heatmap',
                'data': {
                    'matrix': matrix,
                    'x_labels': [f'X{i}' for i in range(size)],
                    'y_labels': [f'Y{i}' for i in range(size)],
                    'values': values
                },
                'options': {
                    'title': 'Numerical Results Heatmap',
                    'color_scheme': 'viridis'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate heatmap data: {e}")
            return {'error': f"Heatmap data generation failed: {str(e)}"}
    
    def export_visualization(self, charts: Dict[str, Any], format_type: str = 'json') -> Dict[str, Any]:
        """
        Export visualization data.
        
        Args:
            charts: Chart data
            format_type: Export format
            
        Returns:
            Exported visualization data
        """
        try:
            if format_type == 'json':
                return charts
            elif format_type == 'html':
                return self._export_to_html(charts)
            elif format_type == 'config':
                return self._export_to_config(charts)
            else:
                logger.warning(f"Unsupported export format: {format_type}")
                return {'error': f"Unsupported export format: {format_type}"}
                
        except Exception as e:
            logger.error(f"Failed to export visualization: {e}")
            return {'error': f"Visualization export failed: {str(e)}"}
    
    def _export_to_html(self, charts: Dict[str, Any]) -> Dict[str, Any]:
        """Export charts to HTML format."""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Physics Simulation Results</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <h1>Physics Simulation Results</h1>
                <p>Generated on: {charts.get('timestamp', 'Unknown')}</p>
                
                <div id="charts">
                    <h2>Summary</h2>
                    <canvas id="summaryChart"></canvas>
                    
                    <h2>Numerical Results</h2>
                    <canvas id="numericalChart"></canvas>
                    
                    <h2>Categorical Results</h2>
                    <canvas id="categoricalChart"></canvas>
                </div>
                
                <script>
                    // Chart.js configuration would go here
                    console.log('Charts data:', {charts});
                </script>
            </body>
            </html>
            """
            
            return {
                'format': 'html',
                'content': html_content,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")
            return {'error': f"HTML export failed: {str(e)}"}
    
    def _export_to_config(self, charts: Dict[str, Any]) -> Dict[str, Any]:
        """Export charts to configuration format."""
        try:
            config = {
                'visualization_config': {
                    'timestamp': charts.get('timestamp', datetime.now().isoformat()),
                    'total_charts': len(charts.get('charts', {})),
                    'chart_types': list(charts.get('charts', {}).keys()),
                    'charts': charts.get('charts', {})
                }
            }
            
            return {
                'format': 'config',
                'content': config,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export to config: {e}")
            return {'error': f"Config export failed: {str(e)}"} 