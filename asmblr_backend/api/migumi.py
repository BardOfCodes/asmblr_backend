"""Migumi animation/state shader generation endpoints."""

from flask import Blueprint, request
import traceback
import geolipi.symbolic as gls
from sysl.utils import recursive_gls_to_sysl
import sysl.symbolic as sls
from asmblr.base import BaseNode
import asmblr.nodes as anodes
from sysl.shader.evaluate import evaluate_to_shader
import migumi.shader
from sysl.shader import DEFAULT_SETTINGS
from sysl.shader_runtime.generate_shader_html import create_shader_html, create_multibuffer_shader_html
from migumi.utils.converter import fix_format, get_expr_and_state, fix_expr_dict
from migumi.shader.compiler import compile_set
from migumi.shader.compile_multipass import compile_set_multipass
from sysl.shader.shader_templates.common import RenderMode

from asmblr_backend.utils import create_response

migumi_bp = Blueprint('migumi', __name__, url_prefix='/api/migumi')


def get_expr_and_state(nodes):
    """
    Extract geometry expressions and state mappings from nodes.
    
    Args:
        nodes: List of evaluated node objects
        
    Returns:
        tuple: (expr_dict, state_map)
    """
    expr_dict = {}
    state_map = {}
    for node in nodes:
        if isinstance(node, anodes.RegisterGeometry):
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
    
    # Sort by keys
    state_sequence = sorted(state_map.keys())
    state_map = {state: state_map[state] for state in state_sequence}
    return expr_dict, state_map


def data_to_shader(data):
    """
    Convert graph data to shader code with informational messages.
    
    Args:
        data: Request payload containing modules and settings
    
    Returns:
        tuple: (all_shader_bundles, messages)
    """
    messages = []
    
    # Extract and validate modules
    modules = data.get("modules", {})
    settings = data.get("shaderSettings", {})
    post_process_shader = settings.pop("post_process_shader", ["part_outline_nobg"])
    render_mode = settings.get("render_mode", RenderMode.DEFAULT)

    if not modules or 'moduleList' not in modules or 'migumi' not in modules['moduleList']:
        raise ValueError("Missing or invalid migumi module data in payload")
    
    verbose = data.get('verbose', False)
    module_data = modules['moduleList']['migumi']
    if verbose:
        messages.append(f"Processing migumi graph with {len(module_data.get('nodes', []))} nodes")
    
    corrected_data = fix_format(module_data)
    node_expressions = BaseNode.from_dict(corrected_data)

    if verbose:
        messages.append("Node graph evaluation completed successfully")

    # Generate shader code
    if not isinstance(node_expressions, list):
        node_expressions = [node_expressions]
    expr_dict, state_map = get_expr_and_state(node_expressions)
    expr_dict = fix_expr_dict(expr_dict, mode=render_mode, add_bounding=False)

    all_shader_bundles = compile_set_multipass(
        expr_dict, 
        state_map, 
        settings=settings,
        post_process_shader=post_process_shader
    )
    
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
        data = request.json or {}
        all_shader_bundles, messages = data_to_shader(data)
        
        # Create HTML visualization
        html_code = create_multibuffer_shader_html(
            all_shader_bundles, 
            show_controls=True, 
            backend="twgl",
            layout_horizontal=True
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
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )


@migumi_bp.route('/generate-twgl-shader', methods=['POST'])
def generate_twgl_shader():
    """Generate TWGL-compatible shader code with configurable settings."""
    try:
        print("Generating TWGL shader")
        data = request.json or {}
        all_shader_bundles, messages = data_to_shader(data)
        
        # Extract shader components from bundles
        if isinstance(all_shader_bundles, tuple):
            shader_code, uniforms, textures = all_shader_bundles
        else:
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
        print(traceback.format_exc())
        return create_response(
            error=error_info,
            status_code=500
        )
