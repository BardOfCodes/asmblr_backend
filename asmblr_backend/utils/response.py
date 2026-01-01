"""Standardized API response utilities."""

from flask import jsonify
from typing import Any, Optional


def create_response(
    content: Optional[Any] = None,
    messages: Optional[list[str]] = None,
    error: Optional[Any] = None,
    status_code: int = 200
):
    """
    Create standardized API response with content, messages, and error handling.
    
    Args:
        content: The main response data (dict or any serializable type)
        messages: List of informational messages to show as notifications
        error: Error information (string or dict with message and traceback)
        status_code: HTTP status code
    
    Returns:
        Flask response tuple with (jsonified data, status_code)
    """
    response_data = {
        "content": content,
        "messages": messages or [],
        "error": error
    }
    
    return jsonify(response_data), status_code

