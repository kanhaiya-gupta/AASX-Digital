"""
Schema Validator
================

Validates database table structures and schemas against expected definitions.
Ensures data integrity and schema consistency.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Set
from datetime import datetime

from .base_validator import BaseValidator

logger = logging.getLogger(__name__)


class SchemaValidator(BaseValidator):
    """Validates database schema structures and table definitions"""
    
    def __init__(self, name: str = "SchemaValidator"):
        """
        Initialize the schema validator.
        
        Args:
            name: Name of the validator
        """
        super().__init__(name)
        self._expected_schemas: Dict[str, Dict[str, Any]] = {}
        self._validation_rules: Dict[str, Dict[str, Any]] = {}
        
    def add_expected_schema(self, table_name: str, schema_definition: Dict[str, Any]) -> None:
        """
        Add an expected schema definition for validation.
        
        Args:
            table_name: Name of the table
            schema_definition: Expected table structure
        """
        self._expected_schemas[table_name] = schema_definition
        self.logger.debug(f"Added expected schema for table: {table_name}")
    
    def add_validation_rule(self, rule_name: str, rule_definition: Dict[str, Any]) -> None:
        """
        Add a custom validation rule.
        
        Args:
            rule_name: Name of the validation rule
            rule_definition: Rule definition and parameters
        """
        self._validation_rules[rule_name] = rule_definition
        self.logger.debug(f"Added validation rule: {rule_name}")
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate the provided schema data.
        
        Args:
            data: Schema data to validate (can be table info, schema definition, etc.)
            context: Optional context information for validation
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            if isinstance(data, dict) and 'table_name' in data:
                # Validate single table schema
                return await self._validate_table_schema(data)
            elif isinstance(data, list):
                # Validate multiple table schemas
                return await self._validate_multiple_table_schemas(data)
            elif isinstance(data, str):
                # Validate table name format
                return await self._validate_table_name(data)
            else:
                self.add_validation_error(
                    'data_type', 
                    f"Unsupported data type for validation: {type(data).__name__}",
                    data
                )
                return False
                
        except Exception as e:
            self.add_validation_error(
                'validation_exception',
                f"Exception during validation: {str(e)}",
                str(e)
            )
            return False
    
    async def _validate_table_schema(self, table_info: Dict[str, Any]) -> bool:
        """Validate a single table schema."""
        table_name = table_info.get('table_name')
        if not table_name:
            self.add_validation_error('table_name', 'Table name is required', table_info)
            return False
        
        # Validate table name format
        if not await self._validate_table_name(table_name):
            return False
        
        # Check if we have an expected schema for this table
        if table_name in self._expected_schemas:
            expected_schema = self._expected_schemas[table_name]
            return await self._validate_against_expected_schema(table_name, table_info, expected_schema)
        
        # Basic schema validation without expected schema
        return await self._validate_basic_table_schema(table_info)
    
    async def _validate_multiple_table_schemas(self, table_schemas: List[Dict[str, Any]]) -> bool:
        """Validate multiple table schemas."""
        all_valid = True
        
        for table_schema in table_schemas:
            if not await self._validate_table_schema(table_schema):
                all_valid = False
        
        return all_valid
    
    async def _validate_table_name(self, table_name: str) -> bool:
        """Validate table name format."""
        if not table_name:
            self.add_validation_error('table_name', 'Table name cannot be empty', table_name)
            return False
        
        if not isinstance(table_name, str):
            self.add_validation_error('table_name', 'Table name must be a string', table_name)
            return False
        
        # Check for valid characters (alphanumeric, underscore only - no hyphens)
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', table_name):
            self.add_validation_error(
                'table_name', 
                'Table name must start with a letter and contain only alphanumeric characters and underscores',
                table_name
            )
            return False
        
        # Check length limits
        if len(table_name) > 63:  # PostgreSQL limit
            self.add_validation_error(
                'table_name',
                'Table name must be 63 characters or less',
                table_name
            )
            return False
        
        return True
    
    async def _validate_against_expected_schema(self, table_name: str, actual_schema: Dict[str, Any], 
                                              expected_schema: Dict[str, Any]) -> bool:
        """Validate actual schema against expected schema."""
        validation_passed = True
        
        # Validate columns
        if 'columns' in expected_schema:
            if 'columns' not in actual_schema:
                self.add_validation_error(
                    'columns',
                    f'Table {table_name} is missing columns definition',
                    actual_schema
                )
                validation_passed = False
            else:
                column_validation = await self._validate_columns(
                    table_name, 
                    actual_schema.get('columns', []), 
                    expected_schema['columns']
                )
                if not column_validation:
                    validation_passed = False
        
        # Validate constraints
        if 'constraints' in expected_schema:
            if 'constraints' not in actual_schema:
                self.add_validation_warning(
                    'constraints',
                    f'Table {table_name} is missing constraints definition',
                    actual_schema
                )
            else:
                constraint_validation = await self._validate_constraints(
                    table_name,
                    actual_schema.get('constraints', []),
                    expected_schema['constraints']
                )
                if not constraint_validation:
                    validation_passed = False
        
        # Validate indexes
        if 'indexes' in expected_schema:
            if 'indexes' not in actual_schema:
                self.add_validation_warning(
                    'indexes',
                    f'Table {table_name} is missing indexes definition',
                    actual_schema
                )
            else:
                index_validation = await self._validate_indexes(
                    table_name,
                    actual_schema.get('indexes', []),
                    expected_schema['indexes']
                )
                if not index_validation:
                    validation_passed = False
        
        return validation_passed
    
    async def _validate_basic_table_schema(self, table_info: Dict[str, Any]) -> bool:
        """Validate basic table schema without expected schema."""
        validation_passed = True
        
        # Check required fields
        required_fields = ['table_name']
        for field in required_fields:
            if field not in table_info:
                self.add_validation_error(field, f'Required field {field} is missing', table_info)
                validation_passed = False
        
        # Validate columns if present
        if 'columns' in table_info:
            columns = table_info['columns']
            if not isinstance(columns, list):
                self.add_validation_error('columns', 'Columns must be a list', columns)
                validation_passed = False
            else:
                for i, column in enumerate(columns):
                    if not isinstance(column, dict):
                        self.add_validation_error(f'columns[{i}]', 'Column must be a dictionary', column)
                        validation_passed = False
                    else:
                        column_validation = await self._validate_column_structure(column, i)
                        if not column_validation:
                            validation_passed = False
        
        return validation_passed
    
    async def _validate_columns(self, table_name: str, actual_columns: List[Dict[str, Any]], 
                               expected_columns: List[Dict[str, Any]]) -> bool:
        """Validate table columns against expected columns."""
        validation_passed = True
        
        # Check column count
        if len(actual_columns) != len(expected_columns):
            self.add_validation_error(
                'column_count',
                f'Table {table_name} has {len(actual_columns)} columns, expected {len(expected_columns)}',
                {'actual': len(actual_columns), 'expected': len(expected_columns)}
            )
            validation_passed = False
        
        # Validate each column
        for i, (actual_col, expected_col) in enumerate(zip(actual_columns, expected_columns)):
            column_name = actual_col.get('name', f'column_{i}')
            
            # Check required column fields
            required_column_fields = ['name', 'type']
            for field in required_column_fields:
                if field not in actual_col:
                    self.add_validation_error(
                        f'columns[{i}].{field}',
                        f'Required column field {field} is missing',
                        actual_col
                    )
                    validation_passed = False
            
            # Validate column structure
            if not await self._validate_column_structure(actual_col, i):
                validation_passed = False
            
            # Check if column matches expected
            if expected_col:
                if not await self._validate_column_against_expected(actual_col, expected_col, i):
                    validation_passed = False
        
        return validation_passed
    
    async def _validate_column_structure(self, column: Dict[str, Any], column_index: int) -> bool:
        """Validate individual column structure."""
        validation_passed = True
        
        # Validate column name
        column_name = column.get('name')
        if not column_name:
            self.add_validation_error(
                f'columns[{column_index}].name',
                'Column name is required',
                column
            )
            validation_passed = False
        elif not isinstance(column_name, str):
            self.add_validation_error(
                f'columns[{column_index}].name',
                'Column name must be a string',
                column_name
            )
            validation_passed = False
        
        # Validate column type
        column_type = column.get('type')
        if not column_type:
            self.add_validation_error(
                f'columns[{column_index}].type',
                'Column type is required',
                column
            )
            validation_passed = False
        elif not isinstance(column_type, str):
            self.add_validation_error(
                f'columns[{column_index}].type',
                'Column type must be a string',
                column_type
            )
            validation_passed = False
        
        # Validate constraints
        if 'not_null' in column and not isinstance(column['not_null'], bool):
            self.add_validation_error(
                f'columns[{column_index}].not_null',
                'not_null constraint must be a boolean',
                column['not_null']
            )
            validation_passed = False
        
        if 'primary_key' in column and not isinstance(column['primary_key'], bool):
            self.add_validation_error(
                f'columns[{column_index}].primary_key',
                'primary_key constraint must be a boolean',
                column['primary_key']
            )
            validation_passed = False
        
        return validation_passed
    
    async def _validate_column_against_expected(self, actual_column: Dict[str, Any], 
                                              expected_column: Dict[str, Any], 
                                              column_index: int) -> bool:
        """Validate actual column against expected column definition."""
        validation_passed = True
        
        # Check column name
        expected_name = expected_column.get('name')
        actual_name = actual_column.get('name')
        if expected_name and actual_name != expected_name:
            self.add_validation_error(
                f'columns[{column_index}].name',
                f'Column name mismatch: expected {expected_name}, got {actual_name}',
                {'expected': expected_name, 'actual': actual_name}
            )
            validation_passed = False
        
        # Check column type
        expected_type = expected_column.get('type')
        actual_type = actual_column.get('type')
        if expected_type and actual_type != expected_type:
            self.add_validation_error(
                f'columns[{column_index}].type',
                f'Column type mismatch: expected {expected_type}, got {actual_type}',
                {'expected': expected_type, 'actual': actual_type}
            )
            validation_passed = False
        
        # Check constraints
        for constraint in ['not_null', 'primary_key', 'unique']:
            if constraint in expected_column:
                expected_value = expected_column[constraint]
                actual_value = actual_column.get(constraint, False)
                if actual_value != expected_value:
                    self.add_validation_error(
                        f'columns[{column_index}].{constraint}',
                        f'Constraint {constraint} mismatch: expected {expected_value}, got {actual_value}',
                        {'expected': expected_value, 'actual': actual_value}
                    )
                    validation_passed = False
        
        return validation_passed
    
    async def _validate_constraints(self, table_name: str, actual_constraints: List[str], 
                                   expected_constraints: List[str]) -> bool:
        """Validate table constraints."""
        validation_passed = True
        
        # Check constraint count
        if len(actual_constraints) < len(expected_constraints):
            self.add_validation_error(
                'constraint_count',
                f'Table {table_name} has {len(actual_constraints)} constraints, expected at least {len(expected_constraints)}',
                {'actual': len(actual_constraints), 'expected': len(expected_constraints)}
            )
            validation_passed = False
        
        # Validate each constraint
        for i, constraint in enumerate(actual_constraints):
            if not isinstance(constraint, str):
                self.add_validation_error(
                    f'constraints[{i}]',
                    'Constraint must be a string',
                    constraint
                )
                validation_passed = False
        
        return validation_passed
    
    async def _validate_indexes(self, table_name: str, actual_indexes: List[Dict[str, Any]], 
                               expected_indexes: List[Dict[str, Any]]) -> bool:
        """Validate table indexes."""
        validation_passed = True
        
        # Check index count
        if len(actual_indexes) < len(expected_indexes):
            self.add_validation_error(
                'index_count',
                f'Table {table_name} has {len(actual_indexes)} indexes, expected at least {len(expected_indexes)}',
                {'actual': len(actual_indexes), 'expected': len(expected_indexes)}
            )
            validation_passed = False
        
        # Validate each index
        for i, index in enumerate(actual_indexes):
            if not isinstance(index, dict):
                self.add_validation_error(
                    f'indexes[{i}]',
                    'Index must be a dictionary',
                    index
                )
                validation_passed = False
            else:
                # Check required index fields
                if 'name' not in index:
                    self.add_validation_error(
                        f'indexes[{i}].name',
                        'Index name is required',
                        index
                    )
                    validation_passed = False
                
                if 'columns' not in index:
                    self.add_validation_error(
                        f'indexes[{i}].columns',
                        'Index columns are required',
                        index
                    )
                    validation_passed = False
        
        return validation_passed
    
    def get_expected_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all expected schemas."""
        return self._expected_schemas.copy()
    
    def get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all validation rules."""
        return self._validation_rules.copy()
    
    def clear_expected_schemas(self) -> None:
        """Clear all expected schemas."""
        self._expected_schemas.clear()
    
    def clear_validation_rules(self) -> None:
        """Clear all validation rules."""
        self._validation_rules.clear()
