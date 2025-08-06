"""
Result processor for physics modeling framework.

This module provides common result processing functionality that all
physics simulations can use for consistent result handling.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Common result processing for all simulations.
    
    This class provides shared functionality for processing simulation results:
    - Result validation
    - Result formatting
    - Result analysis
    - Result export preparation
    """
    
    def __init__(self):
        """Initialize the result processor."""
        logger.debug("Result processor initialized")
    
    def process_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw simulation results.
        
        Args:
            raw_results: Raw results from plugin simulation
            
        Returns:
            Processed results
        """
        try:
            logger.debug(f"Processing {len(raw_results)} raw results")
            
            processed_results = {
                'raw_results': raw_results.copy(),
                'processed_results': {},
                'metadata': {
                    'processing_timestamp': datetime.now().isoformat(),
                    'total_results': len(raw_results)
                }
            }
            
            # Process each result
            for key, value in raw_results.items():
                processed_value = self._process_single_result(key, value)
                processed_results['processed_results'][key] = processed_value
            
            # Add analysis
            processed_results['analysis'] = self._analyze_results(raw_results)
            
            # Add validation
            processed_results['validation'] = self._validate_processed_results(processed_results['processed_results'])
            
            logger.debug("Result processing completed successfully")
            return processed_results
            
        except Exception as e:
            logger.error(f"Result processing failed: {e}")
            return {
                'error': f"Result processing failed: {str(e)}",
                'raw_results': raw_results
            }
    
    def _process_single_result(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Process a single result value.
        
        Args:
            key: Result key
            value: Result value
            
        Returns:
            Processed result
        """
        processed = {
            'original_value': value,
            'processed_value': value,
            'data_type': type(value).__name__,
            'processing_info': {}
        }
        
        # Handle different data types
        if isinstance(value, (int, float)):
            processed.update(self._process_numerical_value(value))
        elif isinstance(value, list):
            processed.update(self._process_list_value(value))
        elif isinstance(value, dict):
            processed.update(self._process_dict_value(value))
        elif isinstance(value, str):
            processed.update(self._process_string_value(value))
        else:
            processed['processing_info']['note'] = f"Unsupported data type: {type(value).__name__}"
        
        return processed
    
    def _process_numerical_value(self, value: float) -> Dict[str, Any]:
        """Process a numerical value."""
        return {
            'processed_value': round(value, 6) if isinstance(value, float) else value,
            'is_finite': self._is_finite_number(value),
            'statistics': {
                'value': value,
                'absolute_value': abs(value),
                'sign': 1 if value >= 0 else -1
            }
        }
    
    def _process_list_value(self, value: List[Any]) -> Dict[str, Any]:
        """Process a list value."""
        processed = {
            'processed_value': value,
            'length': len(value),
            'element_types': list(set(type(item).__name__ for item in value))
        }
        
        # If all elements are numerical, add statistics
        if all(isinstance(item, (int, float)) for item in value):
            processed['statistics'] = {
                'min': min(value),
                'max': max(value),
                'mean': sum(value) / len(value),
                'sum': sum(value)
            }
        
        return processed
    
    def _process_dict_value(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Process a dictionary value."""
        return {
            'processed_value': value,
            'keys': list(value.keys()),
            'key_count': len(value),
            'nested_processing': {
                key: self._process_single_result(key, val)
                for key, val in value.items()
            }
        }
    
    def _process_string_value(self, value: str) -> Dict[str, Any]:
        """Process a string value."""
        return {
            'processed_value': value,
            'length': len(value),
            'is_numeric': value.replace('.', '').replace('-', '').isdigit(),
            'contains_special_chars': any(not c.isalnum() and not c.isspace() for c in value)
        }
    
    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the overall results.
        
        Args:
            results: Raw results dictionary
            
        Returns:
            Analysis results
        """
        analysis = {
            'total_results': len(results),
            'data_types': {},
            'numerical_results': {},
            'categorical_results': {},
            'summary': {}
        }
        
        # Count data types
        for key, value in results.items():
            data_type = type(value).__name__
            analysis['data_types'][data_type] = analysis['data_types'].get(data_type, 0) + 1
        
        # Analyze numerical results
        numerical_values = []
        for key, value in results.items():
            if isinstance(value, (int, float)):
                numerical_values.append(value)
                analysis['numerical_results'][key] = value
        
        if numerical_values:
            analysis['summary']['numerical'] = {
                'count': len(numerical_values),
                'min': min(numerical_values),
                'max': max(numerical_values),
                'mean': sum(numerical_values) / len(numerical_values),
                'range': max(numerical_values) - min(numerical_values)
            }
        
        # Analyze categorical results
        categorical_values = []
        for key, value in results.items():
            if isinstance(value, str):
                categorical_values.append(value)
                analysis['categorical_results'][key] = value
        
        if categorical_values:
            analysis['summary']['categorical'] = {
                'count': len(categorical_values),
                'unique_values': len(set(categorical_values)),
                'most_common': max(set(categorical_values), key=categorical_values.count) if categorical_values else None
            }
        
        return analysis
    
    def _validate_processed_results(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate processed results.
        
        Args:
            processed_results: Processed results dictionary
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checks_passed': 0,
            'checks_failed': 0
        }
        
        # Check for empty results
        if not processed_results:
            validation['valid'] = False
            validation['errors'].append("No processed results found")
            validation['checks_failed'] += 1
        else:
            validation['checks_passed'] += 1
        
        # Check for numerical validity
        for key, result in processed_results.items():
            if result.get('data_type') in ['int', 'float']:
                if not result.get('is_finite', True):
                    validation['warnings'].append(f"Non-finite numerical value in result '{key}'")
                    validation['checks_failed'] += 1
                else:
                    validation['checks_passed'] += 1
        
        # Check for processing errors
        for key, result in processed_results.items():
            if 'error' in result:
                validation['valid'] = False
                validation['errors'].append(f"Processing error in result '{key}': {result['error']}")
                validation['checks_failed'] += 1
        
        return validation
    
    def _is_finite_number(self, value: float) -> bool:
        """Check if a number is finite."""
        try:
            return float(value) == float(value) and abs(float(value)) != float('inf')
        except (ValueError, TypeError):
            return False
    
    def format_results_for_export(self, processed_results: Dict[str, Any], 
                                format_type: str = 'json') -> Dict[str, Any]:
        """
        Format results for export.
        
        Args:
            processed_results: Processed results
            format_type: Export format type
            
        Returns:
            Formatted results
        """
        try:
            if format_type == 'json':
                return self._format_for_json(processed_results)
            elif format_type == 'csv':
                return self._format_for_csv(processed_results)
            elif format_type == 'summary':
                return self._format_for_summary(processed_results)
            else:
                logger.warning(f"Unsupported format type: {format_type}")
                return processed_results
                
        except Exception as e:
            logger.error(f"Failed to format results for export: {e}")
            return {'error': f"Export formatting failed: {str(e)}"}
    
    def _format_for_json(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for JSON export."""
        return {
            'export_format': 'json',
            'timestamp': datetime.now().isoformat(),
            'results': processed_results['processed_results'],
            'metadata': processed_results['metadata'],
            'analysis': processed_results.get('analysis', {}),
            'validation': processed_results.get('validation', {})
        }
    
    def _format_for_csv(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for CSV export."""
        csv_data = {
            'export_format': 'csv',
            'timestamp': datetime.now().isoformat(),
            'headers': ['result_key', 'value', 'data_type', 'processing_info'],
            'rows': []
        }
        
        for key, result in processed_results['processed_results'].items():
            csv_data['rows'].append([
                key,
                str(result.get('processed_value', '')),
                result.get('data_type', ''),
                str(result.get('processing_info', ''))
            ])
        
        return csv_data
    
    def _format_for_summary(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for summary export."""
        return {
            'export_format': 'summary',
            'timestamp': datetime.now().isoformat(),
            'total_results': processed_results['metadata']['total_results'],
            'analysis_summary': processed_results.get('analysis', {}).get('summary', {}),
            'validation_summary': {
                'valid': processed_results.get('validation', {}).get('valid', False),
                'errors_count': len(processed_results.get('validation', {}).get('errors', [])),
                'warnings_count': len(processed_results.get('validation', {}).get('warnings', []))
            }
        } 