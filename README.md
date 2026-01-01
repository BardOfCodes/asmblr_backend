# asmblr_backend

Flask backend for executing commands and generating shaders from a React frontend. Organized with blueprints for different API modules.

## Structure

```
asmblr_backend/
├── scripts/
│   └── app.py                # Main Flask app entry point
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── decor_notes.md            # DecorGumi API documentation
└── asmblr_backend/           # Package
    ├── __init__.py
    ├── utils/                # Shared utilities
    │   ├── __init__.py
    │   └── response.py       # Standardized API responses
    └── api/                  # API modules
        ├── __init__.py       # Blueprint registration
        ├── health.py         # Health check endpoints
        ├── commands.py       # Command execution (dev only)
        ├── system.py         # System info
        ├── geolipi.py        # GeoLIPI shader generation
        ├── sysl.py           # SYSL shader generation
        ├── migumi.py         # Migumi animation shaders
        └── decor_gumi.py     # Polyarc optimization/validation
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install internal packages (adjust paths as needed)
pip install -e ../../../geolipi
pip install -e ../../../sysl
pip install -e ../../../asmblr
pip install -e ../../../migumi
pip install -e ../../../decor_gumi

# Run the server
python scripts/app.py
```

Server runs on `http://localhost:5000`

## API Overview

All responses follow a standardized format:
```json
{
  "content": { ... },
  "messages": ["info message 1", ...],
  "error": null | { "message": "...", "traceback": "...", "type": "..." }
}
```

### Health Check
```
GET /api/health
```
Returns: `{"status": "healthy", "service": "asmblr_backend"}`

### System Info
```
GET /api/system/info    # Platform, Python version, cwd, user
GET /api/system/env     # Safe environment variables
```

### Command Execution (Development Only)

⚠️ **Warning**: These endpoints execute arbitrary shell commands. Only use in trusted environments.

```
POST /api/commands/execute
{
  "command": "echo 'Hello {name}'",
  "params": {"name": "World"},
  "async": false
}

GET /api/commands/status/{command_id}  # For async commands
GET /api/commands/list                  # List all command IDs
```

### GeoLIPI Shader Generation
```
POST /api/geolipi/generate-shader       # Returns HTML visualization
POST /api/geolipi/generate-twgl-shader  # Returns raw TWGL shader code
```

### SYSL Shader Generation
```
POST /api/sysl/generate-shader          # Returns HTML visualization
POST /api/sysl/generate-twgl-shader     # Returns raw TWGL shader code
```

### Migumi Animation Shaders
```
POST /api/migumi/generate-shader        # Returns HTML visualization
POST /api/migumi/generate-twgl-shader   # Returns raw TWGL shader code
```

### DecorGumi Polyarc Optimization
See `decor_notes.md` for detailed API documentation.

```
POST /api/decor_gumi/update-design              # Optimize polyarc for milling
POST /api/decor_gumi/get-morphological-opening  # Get millable region
POST /api/decor_gumi/get-initial-curvature-bounded  # Add corner arcs
POST /api/decor_gumi/validate-design            # Check milling constraints
POST /api/decor_gumi/get-medial-issue-points    # Find narrow regions
POST /api/decor_gumi/get-curvature_issue-points # Find sharp corners
POST /api/decor_gumi/validate-joint             # Validate 3D joint assembly
```

## Adding New API Modules

1. Create new file in `asmblr_backend/api/`
2. Create a Blueprint and define routes
3. Import and register in `asmblr_backend/api/__init__.py`
4. Use `from asmblr_backend.utils import create_response` for consistent responses

Example:
```python
"""My new API module."""
from flask import Blueprint, request
from asmblr_backend.utils import create_response

my_bp = Blueprint('my_api', __name__, url_prefix='/api/my')

@my_bp.route('/endpoint', methods=['POST'])
def my_endpoint():
    try:
        data = request.json or {}
        # ... process data ...
        return create_response(content={"result": "success"})
    except Exception as e:
        return create_response(error=str(e), status_code=500)
```

## Development Notes

- CORS is configured to allow all origins in development. Restrict in production.
- The command execution endpoint has no whitelist by default. Add commands to `ALLOWED_COMMANDS` for production.
- All print statements should be replaced with proper logging for production.
