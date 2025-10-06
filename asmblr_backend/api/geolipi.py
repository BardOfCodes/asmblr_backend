"""Geolipi shader generation endpoints."""

from flask import Blueprint, request, jsonify
import traceback
import geolipi.symbolic as gls
from sysl.utils import recursive_gls_to_sysl
import sysl.symbolic as ssls
from asmblr.base import BaseNode
from sysl.shader.evaluate import evaluate_to_shader
from sysl.shader import DEFAULT_SETTINGS
from sysl.shader_vis.generate_shader_html import create_shader_html

geolipi_bp = Blueprint('geolipi', __name__, url_prefix='/api/geolipi')

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

def data_to_shader(data):
    """
    Convert graph data to shader code with informational messages.
    
    Returns:
        tuple: (shader_code, uniforms, textures, messages)
    """
    messages = []
    
    # Extract and validate modules
    modules = data.get("modules", {})
    if not modules or 'moduleList' not in modules or 'geolipi' not in modules['moduleList']:
        raise ValueError("Missing or invalid GeoLIPI module data in payload")
    
    verbose = data.get('verbose', False)
    expr_dict = modules['moduleList']['geolipi']
    if verbose:
        messages.append(f"Processing GeoLIPI graph with {len(expr_dict.get('nodes', []))} nodes")
    
    # Build and evaluate node graph
    node_graph = BaseNode.from_dict(expr_dict)
    if isinstance(node_graph, list) and len(node_graph) > 1:
        if verbose:
            messages.append(f"Found {len(node_graph)} nodes in the graph. Selecting the first one.")
        node_graph = node_graph[0]

    node_graph.evaluate()
    expr_restored = node_graph.outputs['expr']

    if verbose:
        messages.append("Node graph evaluation completed successfully")

    # Get shader settings from request, use defaults if empty
    shader_settings = data.get('shaderSettings', {})
    if not shader_settings or (isinstance(shader_settings, dict) and len(shader_settings) == 0):
        shader_settings = DEFAULT_SETTINGS
        if verbose:
            messages.append("Using default shader settings")
    else:
        if verbose:
            messages.append(f"Using custom shader settings with {len(shader_settings)} parameters")
    
    # Process GeoLIPI mode settings
    geolipi_settings = data.get('geolipiSettings', {})
    geolipi_mode = geolipi_settings.get('mode', 'primitive')
    
    if geolipi_mode == 'primitive':
        render_mode = shader_settings.get('render_mode', {})
        new_expr, _ = recursive_gls_to_sysl(expr_restored, 2, version=render_mode)
        if verbose:
            messages.append("Converting GeoLIPI expression to CISL primitives (v3)")
    elif geolipi_mode == 'singular':
        new_expr = ssls.MatSolidV3(expr_restored, ssls.NonEmissiveMaterialV3((0.7, 0.7, .7), (0.9,), (0.9,), (0.1,)))
        if verbose:
            messages.append("Wrapping GeoLIPI expression in singular material")
    else:
        raise ValueError(f"Invalid GeoLIPI mode: '{geolipi_mode}'. Must be 'primitive' or 'singular'")

    # Generate shader code
    shader_code, uniforms, textures = evaluate_to_shader(new_expr.sympy(), settings=shader_settings)
    if verbose:
        messages.append(f"Shader generation completed: {len(uniforms)} uniforms, {len(textures)} textures")
    
    return shader_code, uniforms, textures, messages

@geolipi_bp.route('/generate-shader', methods=['POST'])
def generate_shader():
    """Generate shader code with HTML visualization."""
    try:
        # Extract the payload from the request
        data = request.json or {}
        shader_code, uniforms, textures, messages = data_to_shader(data)
        
        # Create HTML visualization
        html_code = create_shader_html(
            shader_code, 
            uniforms, 
            textures, 
            show_controls=True, 
            backend="twgl",
            layout_horizontal=False, 
            allow_overflow=False
        )
        
        messages.append("HTML visualization generated successfully")

        return create_response(
            content={"html": html_code},
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_shader: {e}")
        return create_response(
            error=error_info,
            status_code=500
        )

@geolipi_bp.route('/generate-twgl-shader', methods=['POST'])
def generate_twgl_shader():
    """Generate TWGL-compatible shader code with configurable settings."""
    try:
        print("Generating TWGL shader")
        # Extract the payload from the request
        data = request.json or {}
        shader_code, uniforms, textures, messages = data_to_shader(data)
        
        messages.append("TWGL shader code generated successfully")
        
        # Return the shader code and uniforms dictionary
        return create_response(
            content={
                "shaderCode": shader_code,
                "uniforms": uniforms,
                "textures": textures,
            },
            messages=messages
        )
    
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        print(f"Error in generate_twgl_shader: {e}")
        return create_response(
            error=error_info,
            status_code=500
        )
