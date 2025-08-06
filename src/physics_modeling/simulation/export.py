"""
Export functionality for physics modeling framework.

This module provides common export capabilities that all physics simulations
can use for exporting results in various formats.
"""

import json
import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Export:
    """
    Common export functionality for all simulations.
    
    This class provides shared functionality for exporting simulation results:
    - JSON export
    - CSV export
    - Report generation
    - File export
    """
    
    def __init__(self):
        """Initialize the export component."""
        logger.debug("Export component initialized")
    
    def export_results(self, results: Dict[str, Any], format_type: str = 'json', 
                      file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export simulation results.
        
        Args:
            results: Simulation results
            format_type: Export format (json, csv, report, html)
            file_path: Optional file path for saving
            
        Returns:
            Export result information
        """
        try:
            logger.debug(f"Exporting results in {format_type} format")
            
            if format_type == 'json':
                return self._export_to_json(results, file_path)
            elif format_type == 'csv':
                return self._export_to_csv(results, file_path)
            elif format_type == 'report':
                return self._export_to_report(results, file_path)
            elif format_type == 'html':
                return self._export_to_html(results, file_path)
            else:
                logger.warning(f"Unsupported export format: {format_type}")
                return {'error': f"Unsupported export format: {format_type}"}
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {'error': f"Export failed: {str(e)}"}
    
    def _export_to_json(self, results: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export results to JSON format."""
        try:
            export_data = {
                'export_info': {
                    'format': 'json',
                    'timestamp': datetime.now().isoformat(),
                    'framework_version': '1.0.0'
                },
                'results': results
            }
            
            if file_path:
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                return {
                    'success': True,
                    'format': 'json',
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return as string
                return {
                    'success': True,
                    'format': 'json',
                    'content': json.dumps(export_data, indent=2, ensure_ascii=False),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return {'error': f"JSON export failed: {str(e)}"}
    
    def _export_to_csv(self, results: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export results to CSV format."""
        try:
            # Flatten results for CSV export
            csv_data = []
            
            # Extract processed results
            processed_results = results.get('processed_results', {})
            
            for key, result in processed_results.items():
                row = {
                    'result_key': key,
                    'value': str(result.get('processed_value', '')),
                    'data_type': result.get('data_type', ''),
                    'original_value': str(result.get('original_value', '')),
                    'processing_info': str(result.get('processing_info', ''))
                }
                csv_data.append(row)
            
            if file_path:
                # Save to file
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if csv_data:
                        writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                        writer.writeheader()
                        writer.writerows(csv_data)
                
                return {
                    'success': True,
                    'format': 'csv',
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size,
                    'rows_exported': len(csv_data),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return as string
                import io
                output = io.StringIO()
                if csv_data:
                    writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
                
                return {
                    'success': True,
                    'format': 'csv',
                    'content': output.getvalue(),
                    'rows_exported': len(csv_data),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return {'error': f"CSV export failed: {str(e)}"}
    
    def _export_to_report(self, results: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export results to report format."""
        try:
            # Generate report content
            report_content = self._generate_report_content(results)
            
            if file_path:
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                return {
                    'success': True,
                    'format': 'report',
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return content
                return {
                    'success': True,
                    'format': 'report',
                    'content': report_content,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Report export failed: {e}")
            return {'error': f"Report export failed: {str(e)}"}
    
    def _export_to_html(self, results: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export results to HTML format."""
        try:
            # Generate HTML content
            html_content = self._generate_html_content(results)
            
            if file_path:
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return {
                    'success': True,
                    'format': 'html',
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return content
                return {
                    'success': True,
                    'format': 'html',
                    'content': html_content,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return {'error': f"HTML export failed: {str(e)}"}
    
    def _generate_report_content(self, results: Dict[str, Any]) -> str:
        """Generate report content."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            report = f"""
PHYSICS SIMULATION REPORT
=========================
Generated: {timestamp}
Framework Version: 1.0.0

EXECUTIVE SUMMARY
-----------------
Total Results: {results.get('metadata', {}).get('total_results', 0)}
Processing Timestamp: {results.get('metadata', {}).get('processing_timestamp', 'Unknown')}

RESULTS ANALYSIS
----------------
"""
            
            # Add analysis information
            analysis = results.get('analysis', {})
            if analysis:
                report += f"Data Types: {analysis.get('total_results', 0)} total\n"
                
                # Numerical summary
                numerical_summary = analysis.get('summary', {}).get('numerical', {})
                if numerical_summary:
                    report += f"\nNumerical Results:\n"
                    report += f"  Count: {numerical_summary.get('count', 0)}\n"
                    report += f"  Min: {numerical_summary.get('min', 'N/A')}\n"
                    report += f"  Max: {numerical_summary.get('max', 'N/A')}\n"
                    report += f"  Mean: {numerical_summary.get('mean', 'N/A')}\n"
                    report += f"  Range: {numerical_summary.get('range', 'N/A')}\n"
                
                # Categorical summary
                categorical_summary = analysis.get('summary', {}).get('categorical', {})
                if categorical_summary:
                    report += f"\nCategorical Results:\n"
                    report += f"  Count: {categorical_summary.get('count', 0)}\n"
                    report += f"  Unique Values: {categorical_summary.get('unique_values', 0)}\n"
                    report += f"  Most Common: {categorical_summary.get('most_common', 'N/A')}\n"
            
            # Add validation information
            validation = results.get('validation', {})
            if validation:
                report += f"\nVALIDATION RESULTS\n------------------\n"
                report += f"Valid: {validation.get('valid', False)}\n"
                report += f"Checks Passed: {validation.get('checks_passed', 0)}\n"
                report += f"Checks Failed: {validation.get('checks_failed', 0)}\n"
                
                if validation.get('errors'):
                    report += f"\nErrors:\n"
                    for error in validation['errors']:
                        report += f"  - {error}\n"
                
                if validation.get('warnings'):
                    report += f"\nWarnings:\n"
                    for warning in validation['warnings']:
                        report += f"  - {warning}\n"
            
            # Add detailed results
            report += f"\nDETAILED RESULTS\n----------------\n"
            processed_results = results.get('processed_results', {})
            for key, result in processed_results.items():
                report += f"\n{key}:\n"
                report += f"  Type: {result.get('data_type', 'Unknown')}\n"
                report += f"  Value: {result.get('processed_value', 'N/A')}\n"
                report += f"  Original: {result.get('original_value', 'N/A')}\n"
                
                # Add statistics if available
                stats = result.get('statistics', {})
                if stats:
                    report += f"  Statistics: {stats}\n"
            
            report += f"\nEnd of Report\n"
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report content: {e}")
            return f"Error generating report: {str(e)}"
    
    def _generate_html_content(self, results: Dict[str, Any]) -> str:
        """Generate HTML content."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Physics Simulation Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .result-item {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .success {{ color: green; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Physics Simulation Results</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Framework Version:</strong> 1.0.0</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Total Results:</strong> {results.get('metadata', {}).get('total_results', 0)}</p>
        <p><strong>Processing Timestamp:</strong> {results.get('metadata', {}).get('processing_timestamp', 'Unknown')}</p>
    </div>
"""
            
            # Add analysis section
            analysis = results.get('analysis', {})
            if analysis:
                html += f"""
    <div class="section">
        <h2>Results Analysis</h2>
        <p><strong>Data Types:</strong> {analysis.get('total_results', 0)} total</p>
"""
                
                numerical_summary = analysis.get('summary', {}).get('numerical', {})
                if numerical_summary:
                    html += f"""
        <h3>Numerical Results</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Count</td><td>{numerical_summary.get('count', 0)}</td></tr>
            <tr><td>Min</td><td>{numerical_summary.get('min', 'N/A')}</td></tr>
            <tr><td>Max</td><td>{numerical_summary.get('max', 'N/A')}</td></tr>
            <tr><td>Mean</td><td>{numerical_summary.get('mean', 'N/A')}</td></tr>
            <tr><td>Range</td><td>{numerical_summary.get('range', 'N/A')}</td></tr>
        </table>
"""
                
                categorical_summary = analysis.get('summary', {}).get('categorical', {})
                if categorical_summary:
                    html += f"""
        <h3>Categorical Results</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Count</td><td>{categorical_summary.get('count', 0)}</td></tr>
            <tr><td>Unique Values</td><td>{categorical_summary.get('unique_values', 0)}</td></tr>
            <tr><td>Most Common</td><td>{categorical_summary.get('most_common', 'N/A')}</td></tr>
        </table>
"""
                
                html += "</div>"
            
            # Add validation section
            validation = results.get('validation', {})
            if validation:
                html += f"""
    <div class="section">
        <h2>Validation Results</h2>
        <p><strong>Valid:</strong> <span class="{'success' if validation.get('valid', False) else 'error'}">{validation.get('valid', False)}</span></p>
        <p><strong>Checks Passed:</strong> {validation.get('checks_passed', 0)}</p>
        <p><strong>Checks Failed:</strong> {validation.get('checks_failed', 0)}</p>
"""
                
                if validation.get('errors'):
                    html += "<h3>Errors</h3><ul>"
                    for error in validation['errors']:
                        html += f"<li class='error'>{error}</li>"
                    html += "</ul>"
                
                if validation.get('warnings'):
                    html += "<h3>Warnings</h3><ul>"
                    for warning in validation['warnings']:
                        html += f"<li class='warning'>{warning}</li>"
                    html += "</ul>"
                
                html += "</div>"
            
            # Add detailed results section
            html += """
    <div class="section">
        <h2>Detailed Results</h2>
"""
            
            processed_results = results.get('processed_results', {})
            for key, result in processed_results.items():
                html += f"""
        <div class="result-item">
            <h3>{key}</h3>
            <p><strong>Type:</strong> {result.get('data_type', 'Unknown')}</p>
            <p><strong>Value:</strong> {result.get('processed_value', 'N/A')}</p>
            <p><strong>Original:</strong> {result.get('original_value', 'N/A')}</p>
"""
                
                stats = result.get('statistics', {})
                if stats:
                    html += f"<p><strong>Statistics:</strong> {stats}</p>"
                
                html += "</div>"
            
            html += """
    </div>
</body>
</html>
"""
            
            return html
            
        except Exception as e:
            logger.error(f"Failed to generate HTML content: {e}")
            return f"<html><body><h1>Error</h1><p>Failed to generate HTML: {str(e)}</p></body></html>"
    
    def batch_export(self, results: Dict[str, Any], formats: List[str], 
                    base_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export results in multiple formats.
        
        Args:
            results: Simulation results
            formats: List of export formats
            base_path: Base path for file exports
            
        Returns:
            Batch export results
        """
        try:
            batch_results = {
                'timestamp': datetime.now().isoformat(),
                'formats_requested': formats,
                'exports': {}
            }
            
            for format_type in formats:
                if base_path:
                    # Generate file path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = f"{base_path}/simulation_results_{timestamp}.{format_type}"
                else:
                    file_path = None
                
                export_result = self.export_results(results, format_type, file_path)
                batch_results['exports'][format_type] = export_result
            
            logger.info(f"Batch export completed for {len(formats)} formats")
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch export failed: {e}")
            return {'error': f"Batch export failed: {str(e)}"} 