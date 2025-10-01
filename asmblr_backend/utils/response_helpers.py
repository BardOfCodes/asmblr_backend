"""
Response helper functions for consistent API responses.
"""

from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        data: The response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None, details: Optional[Dict] = None) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
        details: Optional additional error details
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'error_code': error_code,
        'details': details
    }
    return jsonify(response), status_code


def paginated_response(data: list, page: int, per_page: int, total: int, message: str = "Success") -> tuple:
    """
    Create a standardized paginated response.
    
    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }
    return jsonify(response), 200
