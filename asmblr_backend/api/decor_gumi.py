"""Geolipi shader generation endpoints."""

from flask import Blueprint, request, jsonify
import traceback
import geolipi.symbolic as gls
from decor_gumi.arc_opt import (optimize_polyarc, 
                                default_curvature_bounded, minkowski_summed,
                                violating_medial_points, curvature_issue_points,
                                expr_to_api_polyarc)


decorgumi_bp = Blueprint('decor_gumi', __name__, url_prefix='/api/decor_gumi')

def create_response(content=None, messages=None, error=None, status_code=200):
    """
    Create standardized API response with content, messages, and error handling.
    
    Args:
        content: The main response data (dict or any serializable type)
        messages: List of informational messages to show as notifications
        error: Error information (string or dict with message and traceback)
        status_code: HTTP status code
    
    Returns:
        Flask response with standardized format
    """
    response_data = {
        "content": content,
        "messages": messages or [],
        "error": error
    }
    
    return jsonify(response_data), status_code

@decorgumi_bp.route('/update-design', methods=['POST'])
def update_design():
    """Update the design with the given input."""
    try:
        # Extract the payload from the request
        messages = []
        data = request.json or {}
        two_sided = data.get('two_sided', True)
        dilation_rate = data.get('dilation_rate', 0.105)
        mixed_opt = data.get('mixed_opt', False)
        if 'polyarc' in data:
            input_polyarc = data['polyarc']
            # Create HTML visualization
            # output_polyarc = optimize_polyarc(input_polyarc, two_sided, dilation_rate, mixed_opt)
            expr_out = optimize_polyarc(input_polyarc, two_sided, dilation_rate, mixed_opt)
            output_polyarc = expr_to_api_polyarc(expr_out)
        else:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        return create_response(
            content={"polyarc": output_polyarc},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )



@decorgumi_bp.route('/get-morphological-opening', methods=['POST'])
def get_morphological_opening():
    """Get the morphological opening from the database."""
    try:
        # Extract the payload from the request
        messages = []
        data = request.json or {}
        if 'polyarc' in data:
            input_polyarc = data['polyarc']
            dilation_rate = data.get('dilation_rate', 0.105)
            # Create HTML visualization
            output_polyarc = minkowski_summed(input_polyarc, dilation_rate)
        else:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        return create_response(
            content={"polyarc": output_polyarc},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )

@decorgumi_bp.route('/get-initial-curvature-bounded', methods=['POST'])
def get_initial_curvature_bounded():
    """Get the default curvature bounded from the database."""
    try:
        # Extract the payload from the request
        messages = []
        data = request.json or {}
        if 'polyarc' in data:
            input_polyarc = data['polyarc']
            two_sided = data.get('two_sided', True)
            dilation_rate = data.get('dilation_rate', 0.105)
            # Create HTML visualization
            output_polyarc = default_curvature_bounded(input_polyarc, two_sided, dilation_rate)
        else:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        return create_response(
            content={"polyarc": output_polyarc},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )

@decorgumi_bp.route('/validate-design', methods=['POST'])
def validate_design():
    """Validate the design with the given input."""
    try:
        # Extract the payload from the request
        validation_messages = []
        valid_joint = True
        data = request.json or {}
        
        if 'polyarc' not in data:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        
        input_polyarc = data['polyarc']
        two_sided = data.get('two_sided', True)
        dilation_rate = data.get('dilation_rate', 0.105)
        
        # Check for medial axis issues (shape too narrow for mill bit)
        medial_issues = violating_medial_points(input_polyarc, two_sided, dilation_rate)
        if medial_issues and len(medial_issues) > 0:
            valid_joint = False
            validation_messages.append(f"Shape has {len(medial_issues)} region(s) too narrow for mill bit")
        
        # Check for curvature issues (corners too sharp for mill bit)
        curvature_issues = curvature_issue_points(input_polyarc, two_sided, dilation_rate)
        if curvature_issues and len(curvature_issues) > 0:
            valid_joint = False
            validation_messages.append(f"Shape has {len(curvature_issues)} region(s) with curvature too sharp for mill bit")
        
        return create_response(
            content={
                "valid_joint": valid_joint,
                "validation_messages": validation_messages
            }
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in validate_design: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        ) 


@decorgumi_bp.route('/get-medial-issue-points', methods=['POST'])
def get_medial_issue_points():
    """Get the medial issue points from the database."""
    try:
        # Extract the payload from the request
        messages = []
        data = request.json or {}
        if 'polyarc' in data:
            input_polyarc = data['polyarc']
            two_sided = data.get('two_sided', True)
            dilation_rate = data.get('dilation_rate', 0.105)
            # Create HTML visualization
            output_points = violating_medial_points(input_polyarc, two_sided, dilation_rate)
        else:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        return create_response(
            content={"points": output_points},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )


@decorgumi_bp.route('/get-curvature_issue-points', methods=['POST'])
def get_curvature_issue_points():
    """Get the curvature issue points from the database."""

    try:
        # Extract the payload from the request
        messages = []
        data = request.json or {}
        if 'polyarc' in data:
            input_polyarc = data['polyarc']
            two_sided = data.get('two_sided', True)
            dilation_rate = data.get('dilation_rate', 0.105)
            # Create HTML visualization
            output_points = curvature_issue_points(input_polyarc, two_sided, dilation_rate)
        else:
            return create_response(
                error="No input polyarc provided",
                status_code=400
            )
        return create_response(
            content={"points": output_points},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )