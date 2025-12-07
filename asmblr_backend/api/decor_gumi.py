"""Geolipi shader generation endpoints."""

from flask import Blueprint, request, jsonify
import traceback
import io
import geolipi.symbolic as gls
import trimesh
from decor_gumi.arc_opt import (optimize_polyarc, 
                                default_curvature_bounded, minkowski_summed,
                                violating_medial_points, curvature_issue_points,
                                expr_to_api_polyarc)
from decor_gumi.corner_rounding import default_curvature_bound_iterative
from decor_gumi.validation import validate_joint as validate_joint_mesh


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
        dilation_rate = 0.25 # data.get('dilation_rate', 0.105)
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
            dilation_rate = 0.35 # data.get('dilation_rate', 0.105)
            # Create HTML visualization
            output_polyarc = default_curvature_bound_iterative(input_polyarc, two_sided, dilation_rate)
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
            dilation_rate = 0.25 # data.get('dilation_rate', 0.105)
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
            dilation_rate = 0.25 # data.get('dilation_rate', 0.105)
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


@decorgumi_bp.route('/validate-joint', methods=['POST'])
def validate_joint():
    """Validate a joint from mesh data and assembly information."""
    try:
        data = request.json or {}
        
        # Required: mesh data and info dict
        required_keys = ['p_a_obj', 'p_b_obj', 'j_a_obj', 'j_b_obj', 'info']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return create_response(
                error=f"Missing required keys: {', '.join(missing_keys)}",
                status_code=400
            )
        
        p_a_obj = data['p_a_obj']
        p_b_obj = data['p_b_obj']
        j_a_obj = data['j_a_obj']
        j_b_obj = data['j_b_obj']
        info = data['info']
        
        # Optional parameters
        num_samples = data.get('num_samples', 10)
        ratio = data.get('ratio', 1.0)
        
        print(f"[validate_joint] Loading meshes from OBJ content")
        
        # Load meshes from OBJ content strings
        def load_mesh_from_string(obj_content: str) -> trimesh.Trimesh:
            """Load a mesh from OBJ content string."""
            if not obj_content.strip():
                raise ValueError("OBJ content is empty")
            
            # Create a file-like object from the string
            obj_file = io.StringIO(obj_content)
            mesh = trimesh.load(obj_file, file_type='obj', process=False)
            
            # Handle Scene objects
            if isinstance(mesh, trimesh.Scene):
                meshes = [geom for geom in mesh.geometry.values() if isinstance(geom, trimesh.Trimesh)]
                if not meshes:
                    raise ValueError("No valid meshes found in OBJ content")
                elif len(meshes) == 1:
                    mesh = meshes[0]
                else:
                    # Union all meshes in the scene
                    mesh = trimesh.util.concatenate(meshes)
            
            if not isinstance(mesh, trimesh.Trimesh):
                raise ValueError(f"Failed to load mesh from OBJ content. Got type: {type(mesh)}")
            
            # Clean up the mesh
            mesh.merge_vertices()
            mesh.fix_normals()
            
            return mesh
        
        # Load all meshes
        try:
            p_a_mesh = load_mesh_from_string(p_a_obj)
            p_b_mesh = load_mesh_from_string(p_b_obj)
            j_a_mesh = load_mesh_from_string(j_a_obj)
            j_b_mesh = load_mesh_from_string(j_b_obj)
        except Exception as e:
            return create_response(
                error=f"Failed to load meshes: {str(e)}",
                status_code=400
            )
        
        print(f"[validate_joint] Meshes loaded successfully")
        print(f"[validate_joint] Part A: {len(p_a_mesh.vertices)} vertices, {len(p_a_mesh.faces)} faces")
        print(f"[validate_joint] Part B: {len(p_b_mesh.vertices)} vertices, {len(p_b_mesh.faces)} faces")
        print(f"[validate_joint] Joint A: {len(j_a_mesh.vertices)} vertices, {len(j_a_mesh.faces)} faces")
        print(f"[validate_joint] Joint B: {len(j_b_mesh.vertices)} vertices, {len(j_b_mesh.faces)} faces")
        
        # Validate joint using the validation function
        try:
            validation_messages = validate_joint_mesh(
                p_a_mesh=p_a_mesh,
                p_b_mesh=p_b_mesh,
                j_a_mesh=j_a_mesh,
                j_b_mesh=j_b_mesh,
                info=info,
                num_samples=num_samples,
                ratio=ratio
            )
        except Exception as e:
            return create_response(
                error=f"Validation failed: {str(e)}",
                status_code=400
            )
        
        # Determine if joint is valid (no gaps, no intersections)
        valid_joint = True
        for msg in validation_messages:
            if "Has gaps" in msg or "Has intersections" in msg:
                valid_joint = False
                break
        
        return create_response(
            content={
                "valid_joint": valid_joint,
                "validation_messages": validation_messages
            },
            messages=[f"Validated joint assembly"]
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in validate_joint: {e}")
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )