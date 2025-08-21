"""
Data Transformation Utilities

Provides comprehensive data transformation utilities for the AAS Data Modeling Engine.
Includes data format conversion, schema transformation, data cleaning, and validation.
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import io

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"
    PARQUET = "parquet"
    EXCEL = "excel"
    PICKLE = "pickle"
    TEXT = "text"


@dataclass
class TransformationConfig:
    """Configuration for data transformations"""
    preserve_original: bool = True
    validate_schema: bool = True
    handle_missing: str = "drop"  # drop, fill, keep
    missing_fill_value: Any = None
    normalize_types: bool = True
    encoding: str = "utf-8"
    compression: Optional[str] = None


class DataTransformers:
    """Collection of data transformation utilities"""
    
    @staticmethod
    def convert_format(
        data: Any,
        target_format: DataFormat,
        config: Optional[TransformationConfig] = None
    ) -> Any:
        """
        Convert data between different formats
        
        Args:
            data: Input data
            target_format: Target format to convert to
            config: Transformation configuration
            
        Returns:
            Data in target format
        """
        if config is None:
            config = TransformationConfig()
        
        try:
            if target_format == DataFormat.JSON:
                return DataTransformers._to_json(data, config)
            elif target_format == DataFormat.CSV:
                return DataTransformers._to_csv(data, config)
            elif target_format == DataFormat.XML:
                return DataTransformers._to_xml(data, config)
            elif target_format == DataFormat.YAML:
                return DataTransformers._to_yaml(data, config)
            elif target_format == DataFormat.PARQUET:
                return DataTransformers._to_parquet(data, config)
            elif target_format == DataFormat.EXCEL:
                return DataTransformers._to_excel(data, config)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise
    
    @staticmethod
    def _to_json(data: Any, config: TransformationConfig) -> str:
        """Convert data to JSON format"""
        if isinstance(data, (pd.DataFrame, pd.Series)):
            data = data.to_dict(orient='records')
        elif hasattr(data, '__dict__'):
            data = asdict(data)
        
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def _to_csv(data: Any, config: TransformationConfig) -> str:
        """Convert data to CSV format"""
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        elif isinstance(data, list) and data:
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
        
        raise ValueError("Data must be a DataFrame or list of dictionaries for CSV conversion")
    
    @staticmethod
    def _to_xml(data: Any, config: TransformationConfig) -> str:
        """Convert data to XML format"""
        if isinstance(data, dict):
            root = ET.Element("root")
            DataTransformers._dict_to_xml(data, root)
            return ET.tostring(root, encoding='unicode')
        else:
            raise ValueError("Data must be a dictionary for XML conversion")
    
    @staticmethod
    def _dict_to_xml(data: Dict, parent: ET.Element):
        """Recursively convert dictionary to XML"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                DataTransformers._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        DataTransformers._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)
    
    @staticmethod
    def _to_yaml(data: Any, config: TransformationConfig) -> str:
        """Convert data to YAML format"""
        try:
            import yaml
            if isinstance(data, (pd.DataFrame, pd.Series)):
                data = data.to_dict(orient='records')
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ImportError("PyYAML is required for YAML conversion")
    
    @staticmethod
    def _to_parquet(data: Any, config: TransformationConfig) -> bytes:
        """Convert data to Parquet format"""
        if isinstance(data, pd.DataFrame):
            buffer = io.BytesIO()
            data.to_parquet(buffer, compression=config.compression)
            return buffer.getvalue()
        else:
            raise ValueError("Data must be a DataFrame for Parquet conversion")
    
    @staticmethod
    def _to_excel(data: Any, config: TransformationConfig) -> bytes:
        """Convert data to Excel format"""
        if isinstance(data, pd.DataFrame):
            buffer = io.BytesIO()
            data.to_excel(buffer, index=False)
            return buffer.getvalue()
        else:
            raise ValueError("Data must be a DataFrame for Excel conversion")
    
    @staticmethod
    def transform_schema(
        data: Any,
        schema_mapping: Dict[str, str],
        config: Optional[TransformationConfig] = None
    ) -> Any:
        """
        Transform data schema using field mapping
        
        Args:
            data: Input data
            schema_mapping: Dictionary mapping old field names to new field names
            config: Transformation configuration
            
        Returns:
            Data with transformed schema
        """
        if config is None:
            config = TransformationConfig()
        
        try:
            if isinstance(data, pd.DataFrame):
                return DataTransformers._transform_dataframe_schema(data, schema_mapping, config)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return DataTransformers._transform_list_schema(data, schema_mapping, config)
            elif isinstance(data, dict):
                return DataTransformers._transform_dict_schema(data, schema_mapping, config)
            else:
                raise ValueError("Unsupported data type for schema transformation")
        except Exception as e:
            logger.error(f"Schema transformation failed: {e}")
            raise
    
    @staticmethod
    def _transform_dataframe_schema(
        df: pd.DataFrame,
        schema_mapping: Dict[str, str],
        config: TransformationConfig
    ) -> pd.DataFrame:
        """Transform DataFrame schema"""
        # Rename columns according to mapping
        df_transformed = df.rename(columns=schema_mapping)
        
        # Handle missing columns
        missing_columns = set(schema_mapping.values()) - set(df_transformed.columns)
        for col in missing_columns:
            if config.handle_missing == "fill":
                df_transformed[col] = config.missing_fill_value
            elif config.handle_missing == "drop":
                # Column will be missing, which is fine for some use cases
                pass
        
        return df_transformed
    
    @staticmethod
    def _transform_list_schema(
        data_list: List[Dict],
        schema_mapping: Dict[str, str],
        config: TransformationConfig
    ) -> List[Dict]:
        """Transform list of dictionaries schema"""
        transformed_list = []
        
        for item in data_list:
            transformed_item = DataTransformers._transform_dict_schema(item, schema_mapping, config)
            transformed_list.append(transformed_item)
        
        return transformed_list
    
    @staticmethod
    def _transform_dict_schema(
        data_dict: Dict,
        schema_mapping: Dict[str, str],
        config: TransformationConfig
    ) -> Dict:
        """Transform dictionary schema"""
        transformed_dict = {}
        
        for old_key, new_key in schema_mapping.items():
            if old_key in data_dict:
                transformed_dict[new_key] = data_dict[old_key]
            elif config.handle_missing == "fill":
                transformed_dict[new_key] = config.missing_fill_value
        
        return transformed_dict
    
    @staticmethod
    def clean_data(
        data: Any,
        cleaning_rules: Optional[Dict[str, Callable]] = None,
        config: Optional[TransformationConfig] = None
    ) -> Any:
        """
        Clean data using specified rules
        
        Args:
            data: Input data
            cleaning_rules: Dictionary of field names to cleaning functions
            config: Transformation configuration
            
        Returns:
            Cleaned data
        """
        if config is None:
            config = TransformationConfig()
        
        if cleaning_rules is None:
            cleaning_rules = DataTransformers._get_default_cleaning_rules()
        
        try:
            if isinstance(data, pd.DataFrame):
                return DataTransformers._clean_dataframe(data, cleaning_rules, config)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return DataTransformers._clean_list(data, cleaning_rules, config)
            elif isinstance(data, dict):
                return DataTransformers._clean_dict(data, cleaning_rules, config)
            else:
                return data
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            raise
    
    @staticmethod
    def _get_default_cleaning_rules() -> Dict[str, Callable]:
        """Get default data cleaning rules"""
        return {
            "strip_whitespace": lambda x: x.strip() if isinstance(x, str) else x,
            "remove_duplicates": lambda x: list(dict.fromkeys(x)) if isinstance(x, list) else x,
            "normalize_case": lambda x: x.lower() if isinstance(x, str) else x,
            "remove_special_chars": lambda x: ''.join(c for c in str(x) if c.isalnum() or c.isspace()) if isinstance(x, str) else x
        }
    
    @staticmethod
    def _clean_dataframe(
        df: pd.DataFrame,
        cleaning_rules: Dict[str, Callable],
        config: TransformationConfig
    ) -> pd.DataFrame:
        """Clean DataFrame data"""
        df_cleaned = df.copy()
        
        for column in df_cleaned.columns:
            if column in cleaning_rules:
                df_cleaned[column] = df_cleaned[column].apply(cleaning_rules[column])
        
        return df_cleaned
    
    @staticmethod
    def _clean_list(
        data_list: List[Dict],
        cleaning_rules: Dict[str, Callable],
        config: TransformationConfig
    ) -> List[Dict]:
        """Clean list of dictionaries"""
        cleaned_list = []
        
        for item in data_list:
            cleaned_item = DataTransformers._clean_dict(item, cleaning_rules, config)
            cleaned_list.append(cleaned_item)
        
        return cleaned_list
    
    @staticmethod
    def _clean_dict(
        data_dict: Dict,
        cleaning_rules: Dict[str, Callable],
        config: TransformationConfig
    ) -> Dict:
        """Clean dictionary data"""
        cleaned_dict = {}
        
        for key, value in data_dict.items():
            if key in cleaning_rules:
                cleaned_dict[key] = cleaning_rules[key](value)
            else:
                cleaned_dict[key] = value
        
        return cleaned_dict
    
    @staticmethod
    def validate_data(
        data: Any,
        schema: Dict[str, Any],
        config: Optional[TransformationConfig] = None
    ) -> Dict[str, Any]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Schema definition
            config: Transformation configuration
            
        Returns:
            Validation results
        """
        if config is None:
            config = TransformationConfig()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_validations": {}
        }
        
        try:
            if isinstance(data, pd.DataFrame):
                DataTransformers._validate_dataframe(data, schema, validation_results, config)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                DataTransformers._validate_list(data, schema, validation_results, config)
            elif isinstance(data, dict):
                DataTransformers._validate_dict(data, schema, validation_results, config)
            else:
                validation_results["errors"].append("Unsupported data type for validation")
                validation_results["valid"] = False
        except Exception as e:
            validation_results["errors"].append(f"Validation failed: {e}")
            validation_results["valid"] = False
        
        return validation_results
    
    @staticmethod
    def _validate_dataframe(
        df: pd.DataFrame,
        schema: Dict[str, Any],
        validation_results: Dict[str, Any],
        config: TransformationConfig
    ):
        """Validate DataFrame against schema"""
        for column in df.columns:
            if column in schema:
                field_validation = DataTransformers._validate_field(df[column], schema[column])
                validation_results["field_validations"][column] = field_validation
                
                if not field_validation["valid"]:
                    validation_results["valid"] = False
                    validation_results["errors"].extend(field_validation["errors"])
    
    @staticmethod
    def _validate_list(
        data_list: List[Dict],
        schema: Dict[str, Any],
        validation_results: Dict[str, Any],
        config: TransformationConfig
    ):
        """Validate list of dictionaries against schema"""
        for i, item in enumerate(data_list):
            item_validation = DataTransformers._validate_dict(item, schema, validation_results, config)
            if not item_validation["valid"]:
                validation_results["errors"].append(f"Item {i}: {item_validation['errors']}")
    
    @staticmethod
    def _validate_dict(
        data_dict: Dict,
        schema: Dict[str, Any],
        validation_results: Dict[str, Any],
        config: TransformationConfig
    ):
        """Validate dictionary against schema"""
        for field, field_schema in schema.items():
            if field in data_dict:
                field_validation = DataTransformers._validate_field(data_dict[field], field_schema)
                validation_results["field_validations"][field] = field_validation
                
                if not field_validation["valid"]:
                    validation_results["valid"] = False
                    validation_results["errors"].extend(field_validation["errors"])
            elif field_schema.get("required", False):
                validation_results["errors"].append(f"Required field '{field}' is missing")
                validation_results["valid"] = False
    
    @staticmethod
    def _validate_field(value: Any, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual field against schema"""
        field_validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Type validation
        expected_type = field_schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            field_validation["errors"].append(f"Expected type {expected_type}, got {type(value)}")
            field_validation["valid"] = False
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            if "min" in field_schema and value < field_schema["min"]:
                field_validation["errors"].append(f"Value {value} is below minimum {field_schema['min']}")
                field_validation["valid"] = False
            
            if "max" in field_schema and value > field_schema["max"]:
                field_validation["errors"].append(f"Value {value} is above maximum {field_schema['max']}")
                field_validation["valid"] = False
        
        # Length validation for strings and lists
        if hasattr(value, "__len__"):
            if "min_length" in field_schema and len(value) < field_schema["min_length"]:
                field_validation["errors"].append(f"Length {len(value)} is below minimum {field_schema['min_length']}")
                field_validation["valid"] = False
            
            if "max_length" in field_schema and len(value) > field_schema["max_length"]:
                field_validation["errors"].append(f"Length {len(value)} is above maximum {field_schema['max_length']}")
                field_validation["valid"] = False
        
        # Pattern validation for strings
        if isinstance(value, str) and "pattern" in field_schema:
            import re
            if not re.match(field_schema["pattern"], value):
                field_validation["errors"].append(f"Value '{value}' does not match pattern {field_schema['pattern']}")
                field_validation["valid"] = False
        
        return field_validation


# Convenience functions
def convert_format(
    data: Any,
    target_format: DataFormat,
    config: Optional[TransformationConfig] = None
) -> Any:
    """Convenience function for format conversion"""
    return DataTransformers.convert_format(data, target_format, config)


def transform_schema(
    data: Any,
    schema_mapping: Dict[str, str],
    config: Optional[TransformationConfig] = None
) -> Any:
    """Convenience function for schema transformation"""
    return DataTransformers.transform_schema(data, schema_mapping, config)


def clean_data(
    data: Any,
    cleaning_rules: Optional[Dict[str, Callable]] = None,
    config: Optional[TransformationConfig] = None
) -> Any:
    """Convenience function for data cleaning"""
    return DataTransformers.clean_data(data, cleaning_rules, config)


def validate_data(
    data: Any,
    schema: Dict[str, Any],
    config: Optional[TransformationConfig] = None
) -> Dict[str, Any]:
    """Convenience function for data validation"""
    return DataTransformers.validate_data(data, schema, config)
