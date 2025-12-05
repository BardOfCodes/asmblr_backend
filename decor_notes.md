# DecorGumi API Documentation

## Overview

The DecorGumi API provides endpoints for optimizing and validating 2D polyarc shapes for CNC milling constraints. All endpoints are prefixed with `/api/decor_gumi/`.

---

## Data Types

### Polyarc

A **polyarc** is a list of vertices defining a closed 2D polygon with optional arc segments.

**Format:** `List[List[float]]` - A list of `[x, y, bulge]` triplets.

- `x` (float): X coordinate of the vertex
- `y` (float): Y coordinate of the vertex  
- `bulge` (float): Arc parameter for the segment starting at this vertex
  - `0.0` = straight line segment
  - Non-zero = arc segment (positive = counterclockwise, negative = clockwise)
  - `bulge = tan(θ/4)` where θ is the included angle of the arc

**Example:**
```json
{
  "polyarc": [
    [1.0, -0.75, 0.0],
    [1.0, -0.375, 0.0],
    [1.2, -0.375, 0.0],
    [1.2, -0.25, 0.0],
    [1.0, -0.25, 0.0],
    [1.0, 0.75, 0.0],
    [2.7, 0.75, 0.0],
    [2.7, -0.75, 0.0]
  ]
}
```

### Points

A **points** list represents 2D coordinates.

**Format:** `List[List[float]]` - A list of `[x, y]` pairs.

**Example:**
```json
{
  "points": [
    [1.5, 0.3],
    [2.1, -0.2],
    [1.8, 0.5]
  ]
}
```

---

## Standard Response Format

All endpoints return responses in this format:

```json
{
  "content": { ... },      // Main response data (null on error)
  "messages": [ ... ],     // Informational messages (array of strings)
  "error": null | {        // Error info (null on success)
    "message": "string",
    "traceback": "string",
    "type": "string"
  }
}
```

---

## Endpoints

### 1. POST `/api/decor_gumi/update-design`

Optimizes a polyarc to satisfy milling constraints (curvature bounds, medial axis constraints).

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices `[[x, y, bulge], ...]` |
| `two_sided` | `bool` | No | `true` | Whether milling is two-sided (affects curvature constraints) |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius (half of mill bit diameter) |
| `mixed_opt` | `bool` | No | `false` | Enable mixed optimization with medial axis loss |

**Response Content:**
```json
{
  "polyarc": [[x, y, bulge], ...]
}
```

**Example Request:**
```json
{
  "polyarc": [
    [-0.5, -0.25, 0.0],
    [0.5, -0.25, 0.0],
    [0.5, 0.25, 0.0],
    [-0.5, 0.25, 0.0]
  ],
  "two_sided": true,
  "dilation_rate": 0.105
}
```

**Example Response:**
```json
{
  "content": {
    "polyarc": [
      [-0.5, -0.25, 0.105],
      [0.5, -0.25, 0.105],
      [0.5, 0.25, 0.105],
      [-0.5, 0.25, 0.105]
    ]
  },
  "messages": [],
  "error": null
}
```

---

### 2. GET `/api/decor_gumi/get-morphological-opening`

Computes the morphological opening of a polyarc (erosion followed by dilation). This shows the "millable" region.

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius |

**Response Content:**
```json
{
  "polyarc": [[x, y, bulge], ...]
}
```

**Example Request:**
```json
{
  "polyarc": [
    [-0.5, -0.25, 0.0],
    [-0.05, -0.25, 0.0],
    [-0.05, -0.5, 1.0],
    [0.05, -0.5, 0.0],
    [0.05, -0.25, 0.0],
    [0.5, -0.25, 0.0],
    [0.5, 0.25, 0.0],
    [-0.5, 0.25, 0.0]
  ],
  "dilation_rate": 0.1
}
```

---

### 3. GET `/api/decor_gumi/get-initial-curvature-bounded`

Adds corner arcs to a polyarc to satisfy minimum curvature radius constraints (no optimization, just initial rounding).

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices |
| `two_sided` | `bool` | No | `true` | Whether milling is two-sided |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius (determines min corner radius) |

**Response Content:**
```json
{
  "polyarc": [[x, y, bulge], ...]
}
```

**Example Request:**
```json
{
  "polyarc": [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0]
  ],
  "two_sided": true,
  "dilation_rate": 0.105
}
```

---

### 4. GET `/api/decor_gumi/validate-design`

Validates a design for milling constraints. Returns whether the joint is valid and a list of issues found.

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices |
| `two_sided` | `bool` | No | `true` | Whether milling is two-sided |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius |

**Response Content:**
```json
{
  "valid_joint": true | false,
  "validation_messages": ["string", ...]
}
```

- `valid_joint` (bool): `true` if the design passes all milling constraints, `false` otherwise
- `validation_messages` (List[string]): List of issues found (empty if valid)

**Example Request:**
```json
{
  "polyarc": [
    [-0.5, -0.25, 0.0],
    [-0.05, -0.25, 0.0],
    [-0.05, -0.5, 0.0],
    [0.05, -0.5, 0.0],
    [0.05, -0.25, 0.0],
    [0.5, -0.25, 0.0],
    [0.5, 0.25, 0.0],
    [-0.5, 0.25, 0.0]
  ],
  "two_sided": true,
  "dilation_rate": 0.105
}
```

**Example Response (Valid):**
```json
{
  "content": {
    "valid_joint": true,
    "validation_messages": []
  },
  "messages": [],
  "error": null
}
```

**Example Response (Invalid):**
```json
{
  "content": {
    "valid_joint": false,
    "validation_messages": [
      "Shape has 2 region(s) too narrow for mill bit",
      "Shape has 3 region(s) with curvature too sharp for mill bit"
    ]
  },
  "messages": [],
  "error": null
}
```

---

### 5. GET `/api/decor_gumi/get-medial-issue-points`

Returns points on the medial axis where the shape is too narrow for the mill bit.

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices |
| `two_sided` | `bool` | No | `true` | Whether milling is two-sided |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius |

**Response Content:**
```json
{
  "points": [[x, y], ...]
}
```

Returns an empty list `[]` if no issues are found.

**Example Request:**
```json
{
  "polyarc": [
    [-0.5, -0.25, 0.0],
    [-0.05, -0.25, 0.0],
    [-0.05, -0.5, 0.0],
    [0.05, -0.5, 0.0],
    [0.05, -0.25, 0.0],
    [0.5, -0.25, 0.0],
    [0.5, 0.25, 0.0],
    [-0.5, 0.25, 0.0]
  ],
  "two_sided": true,
  "dilation_rate": 0.105
}
```

**Example Response:**
```json
{
  "content": {
    "points": [
      [0.0, -0.35],
      [0.0, -0.40]
    ]
  },
  "messages": [],
  "error": null
}
```

---

### 6. GET `/api/decor_gumi/get-curvature_issue-points`

Returns midpoints of segments where curvature exceeds the allowed maximum (1/dilation_rate).

**Request Body:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `polyarc` | `List[List[float]]` | Yes | - | Input polyarc vertices |
| `two_sided` | `bool` | No | `true` | Whether milling is two-sided |
| `dilation_rate` | `float` | No | `0.105` | Mill bit radius |

**Response Content:**
```json
{
  "points": [[x, y], ...]
}
```

Returns an empty list `[]` if no curvature issues are found. May return `null` if no points could be sampled.

**Example Request:**
```json
{
  "polyarc": [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.5],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0]
  ],
  "two_sided": false,
  "dilation_rate": 0.105
}
```

**Example Response:**
```json
{
  "content": {
    "points": [
      [0.95, 0.5]
    ]
  },
  "messages": [],
  "error": null
}
```

---

## Parameter Reference

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `dilation_rate` | Mill bit radius in model units | `0.105` (default, ~0.21" diameter bit) |
| `two_sided` | Two-sided milling allows cutting from both sides, relaxing some curvature constraints | `true` / `false` |
| `mixed_opt` | Enables additional medial axis optimization during shape optimization | `true` / `false` |

---

## Error Handling

All endpoints return HTTP 400 for missing required fields:
```json
{
  "content": null,
  "messages": [],
  "error": "No input polyarc provided"
}
```

Server errors return HTTP 500 with full traceback:
```json
{
  "content": null,
  "messages": [],
  "error": {
    "message": "Error description",
    "traceback": "Full Python traceback...",
    "type": "ExceptionType"
  }
}
```

