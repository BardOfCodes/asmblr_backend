"""
Command execution endpoints.

WARNING: This module allows arbitrary command execution and should only be used
in trusted development environments. DO NOT deploy to production without
implementing proper command whitelisting and authentication.
"""

import subprocess
import threading
import uuid
from flask import Blueprint, request, jsonify

commands_bp = Blueprint('commands', __name__, url_prefix='/api/commands')

# In-memory storage for async commands
commands = {}

# Allowed commands whitelist (add commands as needed)
# Set to None to allow all commands (DANGEROUS - development only)
ALLOWED_COMMANDS = None  # TODO: Define whitelist for production


def _is_command_allowed(cmd: str) -> bool:
    """Check if a command is in the allowed whitelist."""
    if ALLOWED_COMMANDS is None:
        return True  # Allow all (development mode)
    
    # Check if the base command is in the whitelist
    base_cmd = cmd.split()[0] if cmd.split() else ""
    return base_cmd in ALLOWED_COMMANDS


def run_command(command_id, cmd, params):
    """Execute command and store result."""
    try:
        commands[command_id]['status'] = 'running'
        
        # Simple parameter substitution
        for key, value in params.items():
            cmd = cmd.replace(f'{{{key}}}', str(value))
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        commands[command_id].update({
            'status': 'completed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        })
    except subprocess.TimeoutExpired:
        commands[command_id].update({'status': 'timeout', 'error': 'Command timed out'})
    except Exception as e:
        commands[command_id].update({'status': 'error', 'error': str(e)})


@commands_bp.route('/execute', methods=['POST'])
def execute():
    """
    Execute a command.
    
    WARNING: This endpoint executes arbitrary shell commands.
    Only use in trusted development environments.
    """
    data = request.json
    cmd = data.get('command')
    params = data.get('params', {})
    async_exec = data.get('async', False)
    
    if not cmd:
        return jsonify({'error': 'Command is required'}), 400
    
    # Security check
    if not _is_command_allowed(cmd):
        return jsonify({'error': 'Command not in allowed whitelist'}), 403
    
    if async_exec:
        # Async execution
        command_id = str(uuid.uuid4())
        commands[command_id] = {'command': cmd, 'status': 'pending'}
        
        thread = threading.Thread(target=run_command, args=(command_id, cmd, params))
        thread.daemon = True
        thread.start()
        
        return jsonify({'command_id': command_id, 'status': 'pending'})
    else:
        # Sync execution
        try:
            for key, value in params.items():
                cmd = cmd.replace(f'{{{key}}}', str(value))
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            return jsonify({
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            })
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Command timed out'}), 408
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@commands_bp.route('/status/<command_id>')
def status(command_id):
    """Get command status."""
    if command_id not in commands:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify(commands[command_id])


@commands_bp.route('/list')
def list_commands():
    """List all commands."""
    return jsonify(list(commands.keys()))
