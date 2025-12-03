"""Geolipi shader generation endpoints."""

from flask import Blueprint, request, jsonify
import traceback
import geolipi.symbolic as gls
from sysl.utils import recursive_gls_to_sysl
import sysl.symbolic as sls
from asmblr.base import BaseNode
import asmblr.nodes as anodes
from sysl.shader.evaluate import evaluate_to_shader
import migumi.shader
from sysl.shader import DEFAULT_SETTINGS
from sysl.shader_vis.generate_shader_html import create_shader_html, create_multibuffer_shader_html
from migumi.utils.converter import fix_format, get_expr_and_state, fix_expr_dict
from migumi.shader.compiler import compile_set
from migumi.shader.compile_multipass import compile_set_multipass

migumi_bp = Blueprint('migumi', __name__, url_prefix='/api/migumi')

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

def get_expr_and_state(nodes):
    expr_dict = {}
    state_map = {}
    for node in nodes:
        if isinstance(node, anodes.RegisterGeometry):
            # modify expr so that the "translations beyond "set Material are not included"
            outputs = node.evaluate(None)
            expr = outputs['expr']
            bbox = outputs['bbox']
            expr_name = outputs['name']
            expr_dict[expr_name] = (expr, bbox)
        elif isinstance(node, anodes.RegisterState):
            outputs = node.evaluate(None)
            expr = outputs['expr']
            state = outputs['state']
            state_map[state] = expr
        else:
            pass
            # raise ValueError("Invalid Node Type")
    # sort by keys
    state_sequence = sorted(state_map.keys())
    state_map = {state: state_map[state] for state in state_sequence}
    return expr_dict, state_map


def data_to_shader(data):
    """
    Convert graph data to shader code with informational messages.
    
    Returns:
        tuple: (shader_code, uniforms, textures, messages)
    """
    messages = []
    
    # Extract and validate modules
    modules = data.get("modules", {})
    if not modules or 'moduleList' not in modules or 'migumi' not in modules['moduleList']:
        raise ValueError("Missing or invalid migumi module data in payload")
    
    verbose = data.get('verbose', False)
    data = modules['moduleList']['migumi']
    if verbose:
        messages.append(f"Processing migumi graph with {len(data.get('nodes', []))} nodes")
    
    corrected_data = fix_format(data)
    # Build and evaluate node graph
    node_expressions = BaseNode.from_dict(data)


    if verbose:
        messages.append("Node graph evaluation completed successfully")

    
    # Generate shader code
    if not isinstance(node_expressions, list):
        node_expressions = [node_expressions]
    expr_dict, state_map = get_expr_and_state(node_expressions)
    expr_dict = fix_expr_dict(expr_dict, mode="v4", add_bounding=False)
    # shader_context = ShaderContextManager()
    # shader_code, uniforms, textures = compile_set(expr_dict, state_map)

    settings = {
        "render_mode": "v4",
        "variables": {
            "_ADD_FLOOR_PLANE": False,
            "castShadows": True,
            "_AA": 1,
            "_RAYCAST_MAX_STEPS": 200,
            "resolution": (512, 512),
            "outline_nhbd": 1,

        },
        "set_to_ubo": False,
        "export_params": False,
        # "target": "ShaderToy",
        # "convert_uniforms_to_constants": True,

    }
    all_shader_bundles = compile_set_multipass(expr_dict, state_map, settings=settings,
        post_process_shader=["part_outline_nobg"])
    if verbose:
        messages.append(f"Total {len(all_shader_bundles)} shader bundles generated")
        for shader_bundle in all_shader_bundles:
            uniforms = shader_bundle['uniforms']
            textures = shader_bundle['textures']
            messages.append(f"Shader generation completed: {len(uniforms)} uniforms, {len(textures)} textures")
    
    return all_shader_bundles, messages

@migumi_bp.route('/generate-shader', methods=['POST'])
def generate_shader():
    """Generate shader code with HTML visualization."""
    try:
        # Extract the payload from the request
        data = request.json or {}
        all_shader_bundles, messages = data_to_shader(data)
        
        # Create HTML visualization
        html_code = create_multibuffer_shader_html(all_shader_bundles, show_controls=True, backend="twgl",
        layout_horizontal=True)

        
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
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )

@migumi_bp.route('/generate-twgl-shader', methods=['POST'])
def generate_twgl_shader():
    """Generate TWGL-compatible shader code with configurable settings."""
    # try:
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
    
    # except Exception as e:
    #     error_info = {
    #         "message": str(e),
    #         "traceback": traceback.format_exc(),
    #         "type": type(e).__name__
    #     }
    #     print(f"Error in generate_twgl_shader: {e}")
    #     print(traceback.format_exc())
    #     return create_response(
    #         error=error_info,
    #         status_code=500
    #     )
