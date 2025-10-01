"""
Request validation utilities.
"""

from typing import Dict, List, Any, Optional
from flask import request


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_request_data(required_fields: List[str], optional_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate request JSON data against required and optional fields.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        
    Returns:
        Dictionary containing validated data
        
    Raises:
        ValidationError: If validation fails
    """
    if not request.is_json:
        raise ValidationError("Request must contain JSON data")
    
    data = request.get_json()
    if not data:
        raise ValidationError("Request body cannot be empty")
    
    # Check required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Extract only valid fields
    valid_fields = set(required_fields)
    if optional_fields:
        valid_fields.update(optional_fields)
    
    validated_data = {key: value for key, value in data.items() if key in valid_fields}
    
    return validated_data


def validate_query_params(required_params: List[str], optional_params: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate query parameters.
    
    Args:
        required_params: List of required parameter names
        optional_params: List of optional parameter names
        
    Returns:
        Dictionary containing validated parameters
        
    Raises:
        ValidationError: If validation fails
    """
    # Check required parameters
    missing_params = [param for param in required_params if param not in request.args]
    if missing_params:
        raise ValidationError(f"Missing required parameters: {', '.join(missing_params)}")
    
    # Extract valid parameters
    valid_params = set(required_params)
    if optional_params:
        valid_params.update(optional_params)
    
    validated_params = {}
    for param in valid_params:
        if param in request.args:
            validated_params[param] = request.args.get(param)
    
    return validated_params


def validate_command_params(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate command execution parameters.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary containing validated command parameters
        
    Raises:
        ValidationError: If validation fails
    """
    if 'command' not in data:
        raise ValidationError("Command is required")
    
    command = data['command']
    if not isinstance(command, str) or not command.strip():
        raise ValidationError("Command must be a non-empty string")
    
    # Validate optional parameters
    params = data.get('params', {})
    if not isinstance(params, dict):
        raise ValidationError("Parameters must be a dictionary")
    
    timeout = data.get('timeout')
    if timeout is not None:
        try:
            timeout = int(timeout)
            if timeout <= 0:
                raise ValidationError("Timeout must be a positive integer")
        except (ValueError, TypeError):
            raise ValidationError("Timeout must be a valid integer")
    
    working_dir = data.get('working_dir')
    if working_dir is not None and not isinstance(working_dir, str):
        raise ValidationError("Working directory must be a string")
    
    return {
        'command': command.strip(),
        'params': params,
        'timeout': timeout,
        'working_dir': working_dir
    }
