# Arc API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for local deployment.

## Endpoints

### GET /
**Description**: Serve the main web interface  
**Response**: HTML page with camera interface

**Example**:
```bash
curl http://localhost:8000/
```

---

### POST /scan
**Description**: Process uploaded frame for wall detection  
**Content-Type**: `multipart/form-data`

**Parameters**:
- `file` (required): Image file (JPEG, PNG)

**Response**:
```json
{
  "wall_detected": true,
  "confidence": 0.85,
  "elements_detected": 2,
  "wall_bounds": {
    "x_min": 50,
    "y_min": 80,
    "x_max": 590,
    "y_max": 400,
    "width": 540,
    "height": 320
  },
  "elements": [
    {
      "class": "outlet",
      "bbox": [120, 200, 140, 220],
      "confidence": 0.92,
      "center": [130, 210]
    }
  ]
}
```

**Example**:
```bash
curl -X POST -F "file=@wall_image.jpg" http://localhost:8000/scan
```

---

### POST /detect_objects
**Description**: Detect wall elements in uploaded image  
**Content-Type**: `multipart/form-data`

**Parameters**:
- `file` (required): Image file

**Response**:
```json
{
  "detections": [
    {
      "class": "outlet",
      "bbox": [120, 200, 140, 220],
      "confidence": 0.92,
      "center": [130, 210]
    },
    {
      "class": "light_switch", 
      "bbox": [300, 180, 320, 210],
      "confidence": 0.88,
      "center": [310, 195]
    }
  ],
  "total_elements": 2
}
```

---

### POST /stitch
**Description**: Stitch multiple walls into room model  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "walls": [
    {
      "id": "wall_1",
      "bounds": {...},
      "confidence": 0.85
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "wall_count": 4,
  "room_bounds": {
    "width": 4.2,
    "height": 2.5,
    "depth": 3.8,
    "area": 15.96,
    "volume": 39.9
  }
}
```

---

### GET /export/glb
**Description**: Export room model as GLB file  
**Response**: Binary GLB file

**Example**:
```bash
curl -O http://localhost:8000/export/glb
```

---

### GET /export/obj
**Description**: Export room model as OBJ file  
**Response**: Text OBJ file

**Example**:
```bash
curl -O http://localhost:8000/export/obj
```

---

### GET /materials
**Description**: Get available materials  

**Response**:
```json
{
  "white_paint": {
    "name": "White Paint",
    "type": "paint",
    "color": [255, 255, 255],
    "roughness": 0.8,
    "metallic": 0.0,
    "file": "white_paint.jpg"
  },
  "brick_red": {
    "name": "Red Brick",
    "type": "brick", 
    "color": [200, 90, 84],
    "roughness": 0.9,
    "metallic": 0.0,
    "file": "brick_red.jpg"
  }
}
```

---

### POST /apply_texture
**Description**: Apply texture to wall  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "material_id": "white_paint",
  "wall_id": "wall_1"
}
```

**Response**:
```json
{
  "success": true,
  "material": {
    "name": "White Paint",
    "type": "paint",
    "color": [255, 255, 255]
  },
  "texture_path": "/app/static/textures/white_paint.jpg",
  "applied_to": "wall_mesh"
}
```

---

### GET /health
**Description**: Health check endpoint  

**Response**:
```json
{
  "status": "healthy",
  "service": "Arc AI Wall Scanner"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file format. Please upload JPEG or PNG image."
}
```

### 404 Not Found
```json
{
  "detail": "Export failed - no room model available"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Wall segmentation failed: insufficient image quality"
}
```

## Data Models

### Wall Detection Result
```typescript
interface WallDetectionResult {
  wall_detected: boolean;
  confidence: number;
  elements_detected: number;
  wall_bounds: {
    x_min: number;
    y_min: number;
    x_max: number;
    y_max: number;
    width: number;
    height: number;
  };
  elements: ElementDetection[];
}
```

### Element Detection
```typescript
interface ElementDetection {
  class: "outlet" | "light_switch" | "window" | "door";
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  confidence: number;
  center: [number, number]; // [x, y]
}
```

### Room Model
```typescript
interface RoomModel {
  success: boolean;
  wall_count: number;
  room_bounds: {
    width: number;
    height: number;
    depth: number;
    area: number;
    volume: number;
  };
}
```

### Material Definition
```typescript
interface Material {
  name: string;
  type: "paint" | "wood" | "brick" | "wallpaper" | "concrete";
  color: [number, number, number]; // RGB values
  roughness: number; // 0.0 to 1.0
  metallic: number;  // 0.0 to 1.0
  file: string;      // Texture filename
}
```

## Rate Limits
- `/scan`: 10 requests per minute per IP
- `/detect_objects`: 20 requests per minute per IP
- `/export/*`: 5 requests per minute per IP

## File Size Limits
- Image uploads: 10MB maximum
- Supported formats: JPEG, PNG, WebP
- Recommended resolution: 640x480 to 1920x1080

## WebSocket API (Future)

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Real-time Scanning
```javascript
// Send frame for processing
ws.send(JSON.stringify({
  type: 'scan_frame',
  data: base64ImageData
}));

// Receive results
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  if (result.type === 'wall_detected') {
    // Handle wall detection result
  }
};
```

## SDK Examples

### Python SDK
```python
import requests

class ArcClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def scan_wall(self, image_path):
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/scan", files=files)
            return response.json()
    
    def export_glb(self, output_path="room.glb"):
        response = requests.get(f"{self.base_url}/export/glb")
        with open(output_path, 'wb') as f:
            f.write(response.content)

# Usage
client = ArcClient()
result = client.scan_wall("wall.jpg")
client.export_glb("my_room.glb")
```

### JavaScript SDK
```javascript
class ArcClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async scanWall(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const response = await fetch(`${this.baseUrl}/scan`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }
  
  async exportGLB() {
    const response = await fetch(`${this.baseUrl}/export/glb`);
    return await response.blob();
  }
}

// Usage
const client = new ArcClient();
const result = await client.scanWall(imageFile);
const glbBlob = await client.exportGLB();
```

## Testing

### Unit Tests
```bash
pytest tests/
```

### API Tests
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test scan endpoint with sample image
curl -X POST -F "file=@test_images/wall1.jpg" http://localhost:8000/scan
```

### Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/health

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```