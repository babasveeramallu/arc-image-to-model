# Arc API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (development mode).

## Endpoints

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Arc API"
}
```

### 2. API Info
```
GET /
```

**Response:**
```json
{
  "message": "Arc - Image to Model API",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "api_docs": "/docs",
    "scan_wall": "/api/scan/wall",
    "detect_elements": "/api/detect/elements",
    "stitch_rooms": "/api/stitch/rooms"
  }
}
```

### 3. Scan Wall
```
POST /api/scan/wall
```

**Request:**
- Form data with image file (multipart/form-data)
- Supported formats: JPEG, PNG

**Response:**
```json
{
  "status": "success",
  "message": "Wall detection complete",
  "wall_detected": true,
  "wall_area": 1200.5,
  "confidence": 0.95,
  "wall_mask": "base64_encoded_image",
  "bounds": {
    "x_min": 0,
    "y_min": 0,
    "x_max": 1080,
    "y_max": 1920
  }
}
```

### 4. Detect Elements
```
POST /api/detect/elements
```

**Request:**
- Form data with image file (multipart/form-data)

**Response:**
```json
{
  "status": "success",
  "message": "Element detection complete",
  "elements": [
    {
      "type": "outlet",
      "confidence": 0.92,
      "bbox": [100, 200, 120, 220],
      "position_3d": [0.5, 1.2, 0.0]
    },
    {
      "type": "switch",
      "confidence": 0.88,
      "bbox": [200, 150, 220, 170],
      "position_3d": [1.0, 1.5, 0.0]
    },
    {
      "type": "window",
      "confidence": 0.85,
      "bbox": [300, 100, 500, 300],
      "position_3d": [2.0, 1.5, 0.0]
    },
    {
      "type": "door",
      "confidence": 0.90,
      "bbox": [600, 0, 700, 400],
      "position_3d": [3.5, 2.0, 0.0]
    }
  ],
  "total_elements": 4
}
```

### 5. Stitch Rooms
```
POST /api/stitch/rooms
```

**Request:**
```json
{
  "walls": [
    {
      "image_id": "wall_1",
      "elements": [...],
      "wall_bounds": {...}
    },
    {
      "image_id": "wall_2",
      "elements": [...],
      "wall_bounds": {...}
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Room stitching complete",
  "room_model": {
    "vertices": [...],
    "faces": [...],
    "elements": [...]
  },
  "walls_processed": 2,
  "room_dimensions": {
    "width": 4.5,
    "height": 2.5,
    "depth": 3.0
  },
  "export_url": "/models/room_12345.glb"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "No image provided"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Error processing request"
}
```

## Example Usage (JavaScript/Axios)

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Scan wall
async function scanWall(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await axios.post(`${API_BASE}/api/scan/wall`, formData);
  return response.data;
}

// Detect elements
async function detectElements(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await axios.post(`${API_BASE}/api/detect/elements`, formData);
  return response.data;
}

// Stitch rooms
async function stitchRooms(wallData) {
  const response = await axios.post(`${API_BASE}/api/stitch/rooms`, wallData);
  return response.data;
}
```

## Rate Limiting
Currently no rate limiting (development mode).

## CORS
Currently allows all origins (development mode). Configure for production.

## Interactive Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
