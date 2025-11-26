"""Main FastAPI application for Arc wall scanner."""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
import cv2
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
import json

# Import our utilities
from app.utils.camera import get_frame
from app.utils.depth import estimate_depth
from app.utils.detection import detect_objects
from app.utils.segmentation import segment_wall
from app.utils.geometry import create_wall_from_segmentation, Wall
from app.utils.stitching import RoomStitcher
from app.utils.model_export import ModelExporter
from app.utils.textures import TextureLibrary
from app.config import *

# Initialize FastAPI app
app = FastAPI(
    title="Arc - AI Wall Scanner",
    description="Real-time wall scanning and 3D room modeling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global instances
room_stitcher = RoomStitcher()
model_exporter = ModelExporter()
texture_library = TextureLibrary()

@app.get("/")
async def root():
    """Serve the main web interface."""
    try:
        return HTMLResponse(content=get_html_content())
    except Exception as e:
        return {"message": "Arc AI Wall Scanner", "error": str(e), "status": "running"}

def get_html_content():
    """Get the HTML content for the web interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arc - AI Wall Scanner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            min-height: 100vh; color: #e0e6ed;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; margin-bottom: 30px; }
        header h1 { font-size: 2.5em; color: #00d4ff; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { 
            background: rgba(26, 26, 46, 0.8); border-radius: 15px; padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .panel h2 { color: #fff; margin-bottom: 15px; }
        .camera-container { 
            background: #000; border-radius: 10px; min-height: 300px;
            display: flex; align-items: center; justify-content: center; position: relative;
        }
        video { width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }
        canvas { border-radius: 10px; }
        .controls { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        button { 
            padding: 12px 20px; background: linear-gradient(135deg, #00d4ff, #5b86e5);
            color: white; border: none; border-radius: 8px; cursor: pointer;
            font-weight: 600; transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { background: #333; cursor: not-allowed; transform: none; }
        .status { 
            padding: 15px; border-radius: 8px; margin-bottom: 15px; font-weight: 500;
        }
        .status.success { background: rgba(40, 167, 69, 0.2); color: #4caf50; }
        .status.error { background: rgba(220, 53, 69, 0.2); color: #f44336; }
        .status.loading { background: rgba(0, 212, 255, 0.2); color: #00d4ff; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }
        .stat-box { 
            background: rgba(15, 15, 35, 0.6); padding: 15px; border-radius: 8px; text-align: center;
        }
        .stat-box .label { font-size: 11px; color: #999; margin-bottom: 5px; }
        .stat-box .value { font-size: 18px; font-weight: 700; color: #00d4ff; }
        .materials { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px; }
        .material { 
            aspect-ratio: 1; border-radius: 8px; cursor: pointer; border: 2px solid transparent;
            transition: all 0.3s; position: relative; overflow: hidden;
        }
        .material:hover { border-color: #00d4ff; transform: scale(1.05); }
        .material.selected { border-color: #4caf50; }
        .material span { 
            position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7);
            color: white; font-size: 10px; padding: 4px; text-align: center;
        }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏠 Arc - AI Wall Scanner</h1>
            <p>Real-time wall scanning and 3D room modeling</p>
        </header>

        <div class="grid">
            <div class="panel">
                <h2>📷 Camera & Scanning</h2>
                <div class="status" id="status">Ready to scan</div>
                
                <div class="camera-container">
                    <video id="camera" playsinline autoplay muted style="display: none;"></video>
                    <canvas id="preview" style="display: none;"></canvas>
                    <div id="camera-fallback">📷 Click Start Camera</div>
                </div>

                <div class="controls">
                    <button onclick="startCamera()">Start Camera</button>
                    <button onclick="scanWall()" id="scan-btn" disabled>Scan Wall</button>
                    <button onclick="stopCamera()">Stop</button>
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <div class="label">Walls Scanned</div>
                        <div class="value" id="wall-count">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="label">Elements Found</div>
                        <div class="value" id="element-count">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="label">Confidence</div>
                        <div class="value" id="confidence">0%</div>
                    </div>
                </div>
            </div>

            <div class="panel">
                <h2>🏠 3D Room Model</h2>
                
                <div class="camera-container">
                    <canvas id="model-canvas" width="400" height="300"></canvas>
                </div>

                <div class="controls">
                    <button onclick="stitchRoom()">Build Room</button>
                    <button onclick="exportGLB()">Export GLB</button>
                    <button onclick="exportOBJ()">Export OBJ</button>
                </div>

                <h3 style="margin-top: 20px; color: #fff;">Materials</h3>
                <div class="materials" id="materials"></div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('camera');
        const preview = document.getElementById('preview');
        const statusEl = document.getElementById('status');
        const scanBtn = document.getElementById('scan-btn');
        let wallCount = 0;
        let scannedWalls = [];

        function updateStatus(msg, type = 'loading') {
            statusEl.textContent = msg;
            statusEl.className = 'status ' + type;
        }

        async function startCamera() {
            updateStatus('Starting camera...', 'loading');
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: { ideal: 'environment' }, width: 640, height: 480 } 
                });
                video.srcObject = stream;
                video.style.display = 'block';
                document.getElementById('camera-fallback').style.display = 'none';
                scanBtn.disabled = false;
                updateStatus('Camera ready!', 'success');
            } catch (err) {
                updateStatus('Camera error: ' + err.message, 'error');
            }
        }

        function stopCamera() {
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }
            video.style.display = 'none';
            document.getElementById('camera-fallback').style.display = 'block';
            scanBtn.disabled = true;
            updateStatus('Camera stopped', 'loading');
        }

        async function scanWall() {
            if (!video.srcObject) return;
            
            updateStatus('Scanning wall...', 'loading');
            
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            canvas.toBlob(async (blob) => {
                if (!blob) {
                    updateStatus('❌ Failed to capture image', 'error');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', blob, 'frame.jpg');

                try {
                    const response = await fetch('/scan', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    
                    if (data.wall_detected) {
                        wallCount++;
                        scannedWalls.push(data);
                        updateStatus(`✅ Wall ${wallCount} scanned!`, 'success');
                        document.getElementById('wall-count').textContent = wallCount;
                        document.getElementById('element-count').textContent = data.elements_detected || 0;
                        document.getElementById('confidence').textContent = Math.round(data.confidence * 100) + '%';
                        
                        // Update 3D preview
                        draw3DPreview();
                    } else {
                        updateStatus('🔍 No wall detected - try different angle', 'loading');
                    }
                } catch (err) {
                    console.error('Scan error:', err);
                    updateStatus('❌ Scan failed: ' + err.message, 'error');
                }
            }, 'image/jpeg', 0.8);
        }

        function draw3DPreview() {
            const canvas = document.getElementById('model-canvas');
            const ctx = canvas.getContext('2d');
            
            // Clear canvas
            ctx.fillStyle = '#0f0f23';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw walls based on count
            ctx.strokeStyle = '#00d4ff';
            ctx.lineWidth = 2;
            ctx.fillStyle = 'rgba(0, 212, 255, 0.1)';
            
            if (wallCount === 1) {
                // Single wall
                ctx.fillRect(50, 80, 300, 140);
                ctx.strokeRect(50, 80, 300, 140);
            } else if (wallCount === 2) {
                // Corner
                ctx.fillRect(50, 80, 200, 140);
                ctx.strokeRect(50, 80, 200, 140);
                ctx.fillRect(250, 80, 100, 200);
                ctx.strokeRect(250, 80, 100, 200);
            } else if (wallCount >= 3) {
                // Room
                drawRoom(ctx);
            }
            
            // Add text
            ctx.fillStyle = '#00d4ff';
            ctx.font = '14px sans-serif';
            ctx.fillText(`${wallCount} wall${wallCount !== 1 ? 's' : ''} scanned`, 10, 25);
        }

        function drawRoom(ctx) {
            // Draw 3D room representation
            ctx.beginPath();
            // Floor
            ctx.moveTo(50, 220);
            ctx.lineTo(300, 220);
            ctx.lineTo(350, 180);
            ctx.lineTo(100, 180);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            
            // Walls
            ctx.fillRect(50, 80, 250, 140);
            ctx.strokeRect(50, 80, 250, 140);
        }

        async function stitchRoom() {
            if (scannedWalls.length < 2) {
                updateStatus('Need at least 2 walls to build room', 'error');
                return;
            }

            updateStatus('Building room model...', 'loading');
            
            try {
                const response = await fetch('/stitch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ walls: scannedWalls })
                });
                const data = await response.json();
                
                if (data.success) {
                    updateStatus('✅ Room model built!', 'success');
                } else {
                    updateStatus('❌ Room building failed', 'error');
                }
            } catch (err) {
                updateStatus('❌ Room building error: ' + err.message, 'error');
            }
        }

        async function exportGLB() {
            try {
                const response = await fetch('/export/glb');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'room.glb';
                a.click();
                updateStatus('✅ GLB exported!', 'success');
            } catch (err) {
                updateStatus('❌ Export failed: ' + err.message, 'error');
            }
        }

        async function exportOBJ() {
            try {
                const response = await fetch('/export/obj');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'room.obj';
                a.click();
                updateStatus('✅ OBJ exported!', 'success');
            } catch (err) {
                updateStatus('❌ Export failed: ' + err.message, 'error');
            }
        }

        // Load materials
        async function loadMaterials() {
            try {
                const response = await fetch('/materials');
                const materials = await response.json();
                const container = document.getElementById('materials');
                
                Object.entries(materials).forEach(([id, material]) => {
                    const div = document.createElement('div');
                    div.className = 'material';
                    div.style.backgroundColor = `rgb(${material.color.join(',')})`;
                    div.innerHTML = `<span>${material.name}</span>`;
                    div.onclick = () => selectMaterial(id);
                    container.appendChild(div);
                });
            } catch (err) {
                console.error('Failed to load materials:', err);
            }
        }

        function selectMaterial(id) {
            document.querySelectorAll('.material').forEach(el => el.classList.remove('selected'));
            event.target.classList.add('selected');
        }

        // Initialize
        loadMaterials();
        draw3DPreview();
    </script>
</body>
</html>
    """

@app.post("/scan")
async def scan_frame(file: UploadFile = File(...)):
    """Process uploaded frame for wall detection."""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load image
        frame = cv2.imread(tmp_path)
        if frame is None:
            os.remove(tmp_path)
            raise HTTPException(status_code=400, detail="Could not read image file")
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        os.remove(tmp_path)
        
        # Process frame with error handling
        try:
            segmentation = segment_wall(frame)
        except Exception as e:
            print(f"Segmentation error: {e}")
            segmentation = {"wall_detected": False, "confidence": 0.0, "bounds": None}
            
        try:
            depth_map = estimate_depth(frame)
        except Exception as e:
            print(f"Depth estimation error: {e}")
            depth_map = None
            
        try:
            elements = detect_objects(frame)
        except Exception as e:
            print(f"Object detection error: {e}")
            elements = {"total_elements": 0, "detections": []}
        
        # Create wall if detected
        wall = None
        if segmentation["wall_detected"]:
            try:
                wall = create_wall_from_segmentation(segmentation, depth_map)
                room_stitcher.add_wall(wall)
            except Exception as e:
                print(f"Wall creation error: {e}")
                # Continue without adding wall
        
        return {
            "wall_detected": segmentation["wall_detected"],
            "confidence": segmentation["confidence"],
            "elements_detected": elements["total_elements"],
            "wall_bounds": segmentation["bounds"],
            "elements": elements["detections"]
        }
        
    except Exception as e:
        print(f"Scan endpoint error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/detect_objects")
async def detect_objects_endpoint(file: UploadFile = File(...)):
    """Detect wall elements in uploaded image."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        frame = cv2.imread(tmp_path)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        os.remove(tmp_path)
        
        result = detect_objects(frame)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stitch")
async def stitch_walls(data: Dict[str, Any]):
    """Stitch multiple walls into room model."""
    try:
        # Get current room model
        room_model = room_stitcher.stitch_walls(room_stitcher.walls)
        
        return {
            "success": True,
            "wall_count": len(room_model.walls),
            "room_bounds": room_model.bounds
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/glb")
async def export_glb_endpoint():
    """Export room model as GLB file."""
    try:
        room_model = room_stitcher.stitch_walls(room_stitcher.walls)
        file_path = model_exporter.export_glb(room_model)
        
        if os.path.exists(file_path):
            return FileResponse(file_path, filename="room.glb")
        else:
            raise HTTPException(status_code=404, detail="Export failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/obj")
async def export_obj_endpoint():
    """Export room model as OBJ file."""
    try:
        room_model = room_stitcher.stitch_walls(room_stitcher.walls)
        file_path = model_exporter.export_obj(room_model)
        
        if os.path.exists(file_path):
            return FileResponse(file_path, filename="room.obj")
        else:
            raise HTTPException(status_code=404, detail="Export failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/materials")
async def get_materials():
    """Get available materials."""
    return texture_library.get_available_materials()

@app.post("/apply_texture")
async def apply_texture_endpoint(data: Dict[str, str]):
    """Apply texture to wall."""
    try:
        material_id = data.get("material_id")
        wall_id = data.get("wall_id", "current")
        
        # Find wall and apply texture
        result = texture_library.apply_texture(None, material_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Arc AI Wall Scanner"}

@app.get("/test")
async def test_route():
    """Simple test route."""
    return {"message": "Arc is running!", "status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, debug=DEBUG)