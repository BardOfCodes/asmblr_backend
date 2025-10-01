"""
Data processing module.
Example module demonstrating how to organize data processing API endpoints.
"""

import json
import csv
import io
from typing import Dict, Any, List, Union
from datetime import datetime


class DataProcessingModule:
    """
    Module for data processing operations.
    This is an example of how to structure modules for different API functionalities.
    """
    
    def __init__(self):
        """Initialize the data processing module."""
        self.supported_formats = ['json', 'csv', 'text']
    
    def validate_data(self, data: Any, data_type: str) -> Dict[str, Any]:
        """
        Validate input data based on type.
        
        Args:
            data: Data to validate
            data_type: Expected data type ('json', 'csv', 'text')
            
        Returns:
            Dictionary with validation result
        """
        try:
            if data_type == 'json':
                if isinstance(data, str):
                    json.loads(data)  # Validate JSON string
                elif not isinstance(data, (dict, list)):
                    return {'valid': False, 'error': 'Invalid JSON data type'}
                
            elif data_type == 'csv':
                if isinstance(data, str):
                    # Try to parse CSV string
                    csv.reader(io.StringIO(data))
                elif not isinstance(data, list):
                    return {'valid': False, 'error': 'CSV data must be string or list'}
                
            elif data_type == 'text':
                if not isinstance(data, str):
                    return {'valid': False, 'error': 'Text data must be string'}
            
            else:
                return {'valid': False, 'error': f'Unsupported data type: {data_type}'}
            
            return {'valid': True, 'message': 'Data validation passed'}
            
        except json.JSONDecodeError as e:
            return {'valid': False, 'error': f'Invalid JSON: {str(e)}'}
        except csv.Error as e:
            return {'valid': False, 'error': f'Invalid CSV: {str(e)}'}
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def transform_json(self, data: Union[str, dict, list], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Transform JSON data based on specified operations.
        
        Args:
            data: JSON data to transform
            operations: List of transformation operations
            
        Returns:
            Dictionary with transformation result
        """
        try:
            # Parse JSON string if needed
            if isinstance(data, str):
                parsed_data = json.loads(data)
            else:
                parsed_data = data
            
            result = parsed_data
            
            for operation in operations:
                op_type = operation.get('type')
                
                if op_type == 'filter':
                    # Filter operation for lists
                    if isinstance(result, list):
                        field = operation.get('field')
                        value = operation.get('value')
                        operator = operation.get('operator', 'equals')
                        
                        if operator == 'equals':
                            result = [item for item in result if item.get(field) == value]
                        elif operator == 'contains':
                            result = [item for item in result if value in str(item.get(field, ''))]
                
                elif op_type == 'map':
                    # Map operation to extract specific fields
                    if isinstance(result, list):
                        fields = operation.get('fields', [])
                        result = [{field: item.get(field) for field in fields} for item in result]
                
                elif op_type == 'sort':
                    # Sort operation for lists
                    if isinstance(result, list):
                        field = operation.get('field')
                        reverse = operation.get('reverse', False)
                        result = sorted(result, key=lambda x: x.get(field, ''), reverse=reverse)
                
                elif op_type == 'limit':
                    # Limit operation for lists
                    if isinstance(result, list):
                        limit = operation.get('count', 10)
                        result = result[:limit]
            
            return {
                'success': True,
                'data': result,
                'operations_applied': len(operations)
            }
            
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'Invalid JSON: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Transformation error: {str(e)}'}
    
    def convert_format(self, data: Any, from_format: str, to_format: str) -> Dict[str, Any]:
        """
        Convert data between different formats.
        
        Args:
            data: Data to convert
            from_format: Source format ('json', 'csv', 'text')
            to_format: Target format ('json', 'csv', 'text')
            
        Returns:
            Dictionary with conversion result
        """
        try:
            # Parse source data
            if from_format == 'json':
                if isinstance(data, str):
                    parsed_data = json.loads(data)
                else:
                    parsed_data = data
            
            elif from_format == 'csv':
                if isinstance(data, str):
                    reader = csv.DictReader(io.StringIO(data))
                    parsed_data = list(reader)
                else:
                    parsed_data = data
            
            elif from_format == 'text':
                parsed_data = str(data)
            
            else:
                return {'success': False, 'error': f'Unsupported source format: {from_format}'}
            
            # Convert to target format
            if to_format == 'json':
                result = json.dumps(parsed_data, indent=2)
            
            elif to_format == 'csv':
                if isinstance(parsed_data, list) and parsed_data:
                    output = io.StringIO()
                    if isinstance(parsed_data[0], dict):
                        writer = csv.DictWriter(output, fieldnames=parsed_data[0].keys())
                        writer.writeheader()
                        writer.writerows(parsed_data)
                    else:
                        writer = csv.writer(output)
                        writer.writerows(parsed_data)
                    result = output.getvalue()
                else:
                    result = str(parsed_data)
            
            elif to_format == 'text':
                result = str(parsed_data)
            
            else:
                return {'success': False, 'error': f'Unsupported target format: {to_format}'}
            
            return {
                'success': True,
                'data': result,
                'from_format': from_format,
                'to_format': to_format
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Conversion error: {str(e)}'}
    
    def analyze_data(self, data: Any, data_type: str) -> Dict[str, Any]:
        """
        Analyze data and provide statistics.
        
        Args:
            data: Data to analyze
            data_type: Type of data ('json', 'csv', 'text')
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                'timestamp': datetime.utcnow().isoformat(),
                'data_type': data_type
            }
            
            if data_type == 'json':
                if isinstance(data, str):
                    parsed_data = json.loads(data)
                else:
                    parsed_data = data
                
                analysis.update({
                    'type': type(parsed_data).__name__,
                    'size': len(str(parsed_data)),
                    'structure': self._analyze_json_structure(parsed_data)
                })
            
            elif data_type == 'csv':
                if isinstance(data, str):
                    reader = csv.reader(io.StringIO(data))
                    rows = list(reader)
                else:
                    rows = data
                
                analysis.update({
                    'rows': len(rows),
                    'columns': len(rows[0]) if rows else 0,
                    'has_header': True,  # Assume first row is header
                    'size': len(str(data))
                })
            
            elif data_type == 'text':
                text_data = str(data)
                lines = text_data.split('\n')
                words = text_data.split()
                
                analysis.update({
                    'characters': len(text_data),
                    'lines': len(lines),
                    'words': len(words),
                    'paragraphs': len([line for line in lines if line.strip()])
                })
            
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            return {'success': False, 'error': f'Analysis error: {str(e)}'}
    
    def _analyze_json_structure(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """
        Analyze JSON structure recursively.
        
        Args:
            data: JSON data to analyze
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth
            
        Returns:
            Dictionary with structure analysis
        """
        if current_depth >= max_depth:
            return {'type': type(data).__name__, 'truncated': True}
        
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': len(data),
                'key_names': list(data.keys())[:10],  # First 10 keys
                'values': {key: self._analyze_json_structure(value, max_depth, current_depth + 1) 
                          for key, value in list(data.items())[:5]}  # First 5 values
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'item_types': list(set(type(item).__name__ for item in data[:10])),
                'sample_items': [self._analyze_json_structure(item, max_depth, current_depth + 1) 
                               for item in data[:3]]  # First 3 items
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100] if len(str(data)) > 100 else str(data)
            }
