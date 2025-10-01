# asmblr_backend

Flask backend for executing commands from a React frontend. Organized with blueprints for different API types.

## Structure

```
asmblr_backend/
├── app.py                    # Main Flask app
├── requirements.txt          # Dependencies
├── README.md                # This file
└── asmblr_backend/          # Package
    ├── __init__.py
    └── api/                 # API modules
        ├── __init__.py      # Blueprint registration
        ├── health.py        # Health endpoints
        ├── commands.py      # Command execution
        └── system.py        # System info
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5002`

## API

### Health Check
```
GET /api/health
```

### Execute Command (Sync)
```
POST /api/commands/execute
{
  "command": "echo 'Hello {name}'",
  "params": {"name": "World"}
}
```

### Execute Command (Async)
```
POST /api/commands/execute
{
  "command": "sleep 5 && echo 'Done'",
  "async": true
}
```

### Get Command Status
```
GET /api/commands/status/{command_id}
```

### List Commands
```
GET /api/commands/list
```

### System Info
```
GET /api/system/info
GET /api/system/env
```

## Adding New API Types

1. Create new file in `asmblr_backend/api/`
2. Add blueprint to `asmblr_backend/api/__init__.py`
3. Keep it simple and focused