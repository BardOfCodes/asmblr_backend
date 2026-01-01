"""SYSL shader generation endpoints."""

from flask import Blueprint, request
import traceback
import sysl.symbolic as ssls
from asmblr.base import BaseNode
from sysl.shader.evaluate import evaluate_to_shader
from sysl.shader import DEFAULT_SETTINGS
from sysl.shader_runtime.generate_shader_html import create_shader_html, create_multibuffer_shader_html

from asmblr_backend.utils import create_response

sysl_bp = Blueprint('sysl', __name__, url_prefix='/api/sysl')


def data_to_shader(data, shader_mode="singlepass"):
    """
    Convert graph data to shader code with informational messages.
    
    Args:
        data: Request payload containing modules and settings
        shader_mode: Either "singlepass" or "multipass"
    
    Returns:
        tuple: (all_shader_bundles, messages)
    """
    messages = []
    
    # Extract and validate modules
    modules = data.get("modules", {})
    if not modules or 'moduleList' not in modules or 'sysl' not in modules['moduleList']:
        raise ValueError("Missing or invalid SYSL module data in payload")
    
    verbose = data.get('verbose', False)
    expr_dict = modules['moduleList']['sysl']
    if verbose:
        messages.append(f"Processing SYSL graph with {len(expr_dict.get('nodes', []))} nodes")
    
    # Build and evaluate node graph
    node_graph = BaseNode.from_dict(expr_dict)
    if isinstance(node_graph, list) and len(node_graph) > 1:
        if verbose:
            messages.append(f"Found {len(node_graph)} nodes in the graph. Selecting the first one.")
        node_graph = node_graph[0]

    node_graph.evaluate()
    new_expr = node_graph.outputs['expr']

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
    post_process_shader = shader_settings.pop("post_process_shader", ["part_outline_nobg"])
    # Generate shader code
    all_shader_bundles = evaluate_to_shader(new_expr, settings=shader_settings, mode=shader_mode,
         post_process_shader=post_process_shader)
    
    if verbose:
        messages.append(f"Total {len(all_shader_bundles)} shader bundles generated")
        for shader_bundle in all_shader_bundles:
            uniforms = shader_bundle['uniforms']
            textures = shader_bundle['textures']
            messages.append(f"Shader generation completed: {len(uniforms)} uniforms, {len(textures)} textures")
    
    return all_shader_bundles, messages


@sysl_bp.route('/generate-shader', methods=['POST'])
def generate_shader():
    """Generate shader code with HTML visualization."""
    try:
        data = request.json or {}
        all_shader_bundles, messages = data_to_shader(data, shader_mode="multipass")
        
        # Create HTML visualization
        html_code = create_multibuffer_shader_html(
            all_shader_bundles,
            show_controls=True, 
            backend="twgl",
            layout_horizontal=True, 
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


@sysl_bp.route('/generate-twgl-shader', methods=['POST'])
def generate_twgl_shader():
    """Generate TWGL-compatible shader code with configurable settings."""
    try:
        print("Generating TWGL shader")
        data = request.json or {}
        all_shader_bundles, messages = data_to_shader(data, shader_mode="singlepass")
        
        # Extract shader components from bundles
        # Note: singlepass mode returns a single bundle, not a list
        if isinstance(all_shader_bundles, tuple):
            shader_code, uniforms, textures = all_shader_bundles
        else:
            # Handle case where it's a list of bundles
            shader_bundle = all_shader_bundles[0] if isinstance(all_shader_bundles, list) else all_shader_bundles
            shader_code = shader_bundle.get('shader_code', '')
            uniforms = shader_bundle.get('uniforms', {})
            textures = shader_bundle.get('textures', {})
        
        messages.append("TWGL shader code generated successfully")
        
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
